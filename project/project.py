import os
import datetime

MOVIE_TXT  = "MovieInfo.dat"
SCREEN_TXT = "ScreeningInfo.dat"
LOG_TXT    = "MovieLog.dat"
REPORT_DIR = "report"
REPORT_TXT = "report/report.txt"

HALL_CAPACITY = {1: 200, 2: 180, 3: 150, 4: 100}

GENRES = {
    "Action","Comedy","Horror","Romance","Drama","Sci-Fi","Thriller",
    "Animation","Adventure","Crime","Fantasy","Mystery","Family"
}

def now():
    return datetime.datetime.now().isoformat(sep=" ", timespec="seconds")

def now_ts():
    return int(datetime.datetime.now().timestamp())

def pause():
    input("\nกด Enter เพื่อดำเนินการต่อ...")

def _parse_movie_line(s: str):
    parts = s.split()
    if len(parts) < 8:
        return None
    try:
        movie_id = int(parts[0])
        duration = int(parts[2])
        price = float(parts[3])
    except:
        return None
    status = parts[1]
    if len(parts) >= 9:
        title = parts[4]
        genre = parts[5]
        rating = parts[6]
        created_at = parts[7]
        updated_at = parts[8]
    else:
        title_token = parts[4]
        if "_" in title_token:
            tokens = title_token.split("_")
            if len(tokens) >= 2:
                genre = tokens[-1]
                title = "_".join(tokens[:-1])
            else:
                genre = "Unknown"
                title = title_token
        else:
            genre = "Unknown"
            title = title_token
        rating = parts[5]
        created_at = parts[6]
        updated_at = parts[7]
    return {
        "movie_id": movie_id,
        "status": status,
        "duration": duration,
        "price": price,
        "title": title,
        "genre": genre,
        "rating": rating,
        "created_at": created_at,
        "updated_at": updated_at,
    }

def read_movies():
    rows = []
    with open(MOVIE_TXT, "r", encoding="utf-8") as f:
        header = True
        for line in f:
            s = line.strip()
            if not s: continue
            if header:
                header = False
                if s and s[0].isdigit():
                    rec = _parse_movie_line(s)
                    if rec: rows.append(rec)
                continue
            rec = _parse_movie_line(s)
            if rec: rows.append(rec)
    return rows

def _format_title_for_write(title: str):
    return title.replace(" ", "_")

def write_movies(rows):
    with open(MOVIE_TXT, "w", encoding="utf-8") as f:
        f.write("movie_id status duration_min ticket_price title genre rating created_at updated_at\n")
        for m in rows:
            title_token = _format_title_for_write(m['title'])
            f.write(f"{m['movie_id']} {m['status']} {m['duration']} {m['price']:.2f} {title_token} {m['genre']} {m['rating']} {m['created_at']} {m['updated_at']}\n")

def read_screens():
    rows = []
    with open(SCREEN_TXT, "r", encoding="utf-8") as f:
        header = True
        for line in f:
            s = line.strip()
            if not s: continue
            if header:
                header = False
                if s and s[0].isdigit():
                    parts = s.split()
                    if len(parts) >= 5:
                        rows.append({
                            "screening_id": int(parts[0]),
                            "movie_id": int(parts[1]),
                            "hall": int(parts[2]),
                            "capacity": int(parts[3]),
                            "booked": int(parts[4]),
                            "status": parts[5] if len(parts) >= 6 else "Active",
                        })
                continue
            parts = s.split()
            if len(parts) < 5: continue
            rows.append({
                "screening_id": int(parts[0]),
                "movie_id": int(parts[1]),
                "hall": int(parts[2]),
                "capacity": int(parts[3]),
                "booked": int(parts[4]),
                "status": parts[5] if len(parts) >= 6 else "Active",
            })
    return rows

def write_screens(rows):
    with open(SCREEN_TXT, "w", encoding="utf-8") as f:
        f.write("screening_id movie_id hall capacity booked status\n")
        for s in rows:
            f.write(f"{s['screening_id']} {s['movie_id']} {s['hall']} {s['capacity']} {s['booked']} {s['status']}\n")

def _movie_by_id(movie_id: int):
    for m in read_movies():
        if m["movie_id"] == movie_id:
            return m
    return None

def append_movie_log(op_code: int, movie_id: int):
    m = _movie_by_id(movie_id)
    if not m:
        return
    status_bit = "1" if str(m.get("status", "")).lower().startswith("a") else "0"

    booked_sum = 0
    for s in read_screens():
        if s["movie_id"] == movie_id and str(s.get("status", "")).lower().startswith("a"):
            booked_sum += s.get("booked", 0)

    revenue_after = float(m["price"]) * float(booked_sum)

    with open(LOG_TXT, "a", encoding="utf-8") as f:
        f.write(
            f"{now_ts()} {op_code} {movie_id} {status_bit} "
            f"{int(m['duration'])} {float(m['price']):.2f} {revenue_after:.2f}\n"
        )


def input_int(prompt, minv=None, maxv=None):
    while True:
        x = input(prompt).strip()
        try:
            v = int(x)
            if minv is not None and v < minv:
                print("ค่าน้อยเกินไป"); continue
            if maxv is not None and v > maxv:
                print("ค่ามากเกินไป"); continue
            return v
        except:
            print("กรุณาใส่ตัวเลข")

def input_float(prompt, minv=None, maxv=None):
    while True:
        x = input(prompt).strip()
        try:
            v = float(x)
            if minv is not None and v < minv:
                print("ค่าน้อยเกินไป"); continue
            if maxv is not None and v > maxv:
                print("ค่ามากเกินไป"); continue
            return v
        except:
            print("กรุณาใส่ตัวเลข")

def input_str(prompt, allow_empty=False, maxlen=None):
    while True:
        s = input(prompt).strip()
        if not s and not allow_empty:
            print("ห้ามเว้นว่าง"); continue
        if maxlen and len(s) > maxlen:
            print("ยาวเกินไป"); continue
        return s

def get_capacity_for_hall(hall: int):
    return HALL_CAPACITY.get(hall)

def add_movie():
    view_all()
    movies = read_movies()
    screens = read_screens()

    movie_id = input_int("Movie ID (ใหม่): ", 1)
    if any(m["movie_id"] == movie_id for m in movies):
        print("Movie ID ซ้ำ")
        return

    title  = input_str("Title: ", 100)
    genre  = input_str("Genre: ", 30)
    rating = input_str("Rating: ", 10)
    dur    = input_int("Duration (mins): ", 1)
    price  = input_float("Ticket Price: ", 0.0)

    today = datetime.date.today().isoformat()
    movies.append({
        "movie_id": movie_id,
        "title": title,
        "genre": genre,
        "rating": rating,
        "duration": dur,
        "price": price,
        "status": "Active",  
        "created_at": today,
        "updated_at": today
    })
    write_movies(movies)
    append_movie_log(1, movie_id)

    print(f"\nเพิ่ม Movie {movie_id} : {title} (Active)\n")
    view_all()
    while True:
        print("กรุณาเพิ่มรอบฉายสำหรับหนังนี้อย่างน้อย 1 รอบ:")
        screening_id = input_int("Screening ID: ", 1)
        if any(s["screening_id"] == screening_id for s in screens):
            print("Screening ID ซ้ำ กรุณาใส่ใหม่")
            continue  
        hall = input_int("Hall (1-4): ", 1, 4)
        cap  = HALL_CAPACITY.get(hall, 0)
        booked = input_int(f"Booked (0-{cap}): ", 0, cap)

        screens.append({
            "screening_id": screening_id,
            "movie_id": movie_id,
            "hall": hall,
            "capacity": cap,
            "booked": booked,
            "status": "Active"
        })
        write_screens(screens)
        append_movie_log(1, movie_id)

        print(f"เพิ่ม Screening {screening_id} ของหนัง {title} เรียบร้อย\n")
        break 

    _print_view_by_movie_id(movie_id)
    pause()


def add_screening():
    view_all()
    movies = read_movies()
    if not movies:
        return
    screens = read_screens()
    movie_id = input_int("กรอก Movie ID ที่ต้องการผูกกับรอบฉาย: ", 1)
    if not any(m["movie_id"] == movie_id for m in movies):
        print("ไม่พบ Movie ID"); return
    screening_id = input_int("Screening ID: ", 1)
    if any(s["screening_id"] == screening_id for s in screens):
        print("มี Screening ID นี้แล้ว"); return
    while True:
        hall = input_int("Hall(1-4): ", 1)
        cap = get_capacity_for_hall(hall)
        if cap is None:
            print("Hall นี้ยังไม่ถูกกำหนดความจุ"); continue
        break
    booked = input_int(f"Booked (0-{cap}): ", 0, cap)
    screens.append({
        "screening_id": screening_id,
        "movie_id": movie_id,
        "hall": hall,
        "capacity": cap,
        "booked": booked,
        "status": "Active",
    })
    write_screens(screens)
    append_movie_log(1, movie_id)
    print("เพิ่มรอบฉายแล้ว\n")
    view_all()
    pause()

def _movie_title(movie_id: int):
    m = _movie_by_id(movie_id)
    return m["title"] if m else "(ไม่พบชื่อ)"

def _print_view_by_movie_id(mid: int):
    pairs = [(s, m) for (s, m) in _join_for_view_left() if m["movie_id"] == mid]
    pairs = [p for p in pairs if (p[0] is None) or (p[0]["status"] == "Active")]
    if not pairs:
        print("ไม่พบข้อมูล")
        return
    print(_header())
    for s, m in pairs:
        print(_render_row(s, m))
    print("----------------------------------------------------------------------------------------------------------------------------------------------------------------")


def update_movie():
    print("\nข้อมูลปัจจุบัน:")
    view_all()
    print("")

    movies = read_movies()
    movie_id = input_int("Movie ID ที่ต้องการแก้ไข: ", 1)
    idx = next((i for i, mm in enumerate(movies) if mm["movie_id"] == movie_id), None)
    if idx is None:
        print("ไม่พบ Movie นี้")
        return

    m = movies[idx]
    print(f"กำลังแก้ไข Movie {m['movie_id']} : {m['title']} กด 'Enter' หากไม่ต้องการแก้ไข")

    t = input_str(f"Title [{m['title']}]: ", allow_empty=True)
    g = input_str(f"Genre [{m['genre']}]: ", allow_empty=True)
    r = input_str(f"Rating [{m['rating']}]: ", allow_empty=True)
    d = input_str(f"Duration(mins) [{m['duration']}]: ", allow_empty=True)
    p = input_str(f"Ticket price [{m['price']:.2f}]: ", allow_empty=True)
    s = input_str(f"Status (Active/Deleted) [{m['status']}]: ", allow_empty=True)

    if t: m["title"] = t
    if g: m["genre"] = g
    if r: m["rating"] = r
    if d:
        try:
            dv = int(d)
            if dv > 0:
                m["duration"] = dv
        except:
            print("ข้ามการแก้ Duration (รูปแบบไม่ถูกต้อง)")
    if p:
        try:
            pv = float(p)
            if pv >= 0:
                m["price"] = pv
        except:
            print("ข้ามการแก้ Price (รูปแบบไม่ถูกต้อง)")
    if s:
        m["status"] = "Active" if s.lower().startswith("a") else "Deleted"

    m["updated_at"] = datetime.date.today().isoformat()
    movies[idx] = m
    write_movies(movies)
    append_movie_log(2, movie_id)

    print(f"\nอัปเดตเรียบร้อย: Movie {m['movie_id']} : {m['title']}\n")
    _print_view_by_movie_id(movie_id)
    pause()


def update_screening():
    print("\nข้อมูลปัจจุบัน:")
    view_all()
    print("")

    screens = read_screens()
    scr_id = input_int("Screening ID ที่ต้องการแก้ไข: ", 1)
    idx = next((i for i, ss in enumerate(screens) if ss["screening_id"] == scr_id), None)
    if idx is None:
        print("ไม่พบ Screening นี้")
        return

    s = screens[idx]
    title = _movie_title(s["movie_id"])
    print(f"กำลังแก้ไข Screening {s['screening_id']} ของหนัง {title} (Movie {s['movie_id']})")

    h = input_str(f"Hall [{s['hall']}]: ", allow_empty=True)
    b = input_str(f"Booked [{s['booked']}]: ", allow_empty=True)
    st = input_str(f"Status (Active/Deleted) [{s['status']}]: ", allow_empty=True)

    if h:
        try:
            hv = int(h)
            if hv > 0:
                cap = HALL_CAPACITY.get(hv)
                if cap is None:
                    print("Hall นี้ยังไม่ถูกกำหนดความจุ — ข้ามการแก้ Hall")
                else:
                    s["hall"] = hv
                    s["capacity"] = cap
                    if s["booked"] > cap:
                        s["booked"] = cap
        except:
            print("ข้ามการแก้ Hall (รูปแบบไม่ถูกต้อง)")

    if b:
        try:
            bv = int(b)
            if 0 <= bv <= s["capacity"]:
                s["booked"] = bv
            else:
                print(f"ค่าจองต้องอยู่ระหว่าง 0..{s['capacity']} — ข้ามการแก้ Booked")
        except:
            print("ข้ามการแก้ Booked (รูปแบบไม่ถูกต้อง)")

    if st:
        s["status"] = "Active" if st.lower().startswith("a") else "Deleted"

    screens[idx] = s
    write_screens(screens)
    append_movie_log(2, s["movie_id"])

    print(f"\nอัปเดตเรียบร้อย: Screening {s['screening_id']} ของหนัง {title}\n")
    _print_view_by_movie_id(s["movie_id"])
    pause()

def delete_menu():
    print("-----------------------------")
    print("1) ลบ Movie (ตั้งสถานะเป็น Deleted)")
    print("2) ลบ Movie ออกจากข้อมูลจริง (Hard delete)")
    print("0) Back")
    print("-----------------------------")
    ch = input_int("เลือกเมนู: ", 0, 3)
    if ch == 0:
        return

    print("\nข้อมูลปัจจุบัน:")
    view_all()
    print("")

    if ch == 1:  
        movies = read_movies()
        movie_id = input_int("Movie ID ที่ต้องการลบ (soft delete): ", 1)
        idx = next((i for i,m in enumerate(movies) if m["movie_id"]==movie_id), None)
        if idx is None:
            print("ไม่พบ Movie นี้"); return
        title = movies[idx]["title"]
        print(f"จะตั้งสถานะ Deleted ให้ Movie {movie_id} : {title}")
        movies[idx]["status"]="Deleted"
        movies[idx]["updated_at"]=datetime.date.today().isoformat()
        write_movies(movies)
        append_movie_log(3, movie_id)
        print(f"ตั้งสถานะ Deleted แล้ว: Movie {movie_id} : {title}")


    elif ch == 2:  
        movies = read_movies()
        screens_all = read_screens()
        movie_id = input_int("Movie ID ที่ต้องการลบออกจากข้อมูลจริง: ", 1)
        m = next((mm for mm in movies if mm["movie_id"] == movie_id), None)
        if not m:
            print("ไม่พบ Movie นี้")
            return
        title = m["title"]
        confirm = input_str(f"ยืนยันลบ Movie {movie_id} : {title} ออกจากทุกไฟล์? (Y/N): ").lower()
        if confirm not in ("y","yes"):
            print("ยกเลิกการลบ")
            return

        movies = [mm for mm in movies if mm["movie_id"] != movie_id]
        write_movies(movies)

        screens = [s for s in screens_all if s["movie_id"] != movie_id]
        write_screens(screens)

        if os.path.exists(LOG_TXT):
            with open(LOG_TXT, "r", encoding="utf-8") as f:
                lines = f.readlines()
            with open(LOG_TXT, "w", encoding="utf-8") as f:
                for line in lines:
                    parts = line.strip().split()
                    if not parts: continue
                    if len(parts) >= 3 and parts[2].isdigit() and int(parts[2]) == movie_id:
                        continue
                    f.write(line)

        print(f"ลบเรียบร้อย: Movie {movie_id} : {title} ออกจากทุกไฟล์แล้ว")
        pause()



def _header():
    return (
        "----------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
        "| ScreeningID | MovieID | Title                  | Genre    | Rating | Hall | duration(min)     | Capacity | Booked | Ticket Price |Revenue(THB/day)|Status    |\n"
        "----------------------------------------------------------------------------------------------------------------------------------------------------------------"
    )

def _fmt_money(v): 
    return f"{v:,.2f}"

def _join_for_view_left():
    movies = read_movies()
    screens = read_screens()
    by_movie = {}
    for s in screens:
        by_movie.setdefault(s["movie_id"], []).append(s)
    out = []
    for m in movies:
        lst = by_movie.get(m["movie_id"])
        if not lst:
            out.append((None, m))
        else:
            for s in lst:
                out.append((s, m))
    return out

def _render_row(s, m):
    title = m["title"].replace("_", " ")
    if len(title) > 22: title = title[:22]
    if s is None:
        screening_id = "-"
        hall = "-"
        capacity = 0
        booked = 0
    else:
        screening_id = s["screening_id"]
        hall = s["hall"]
        capacity = s["capacity"]
        booked = s["booked"]
    revenue = (m["price"] * booked) if s is not None else 0.0
    return (
        f"| {str(screening_id).ljust(11)} | "
        f"{str(m['movie_id']).ljust(7)} | "
        f"{title.ljust(22)} | "
        f"{m['genre'][:8].ljust(8)} | "
        f"{m['rating'][:4].ljust(6)} | "
        f"{str(hall).ljust(4)} | "
        f"{str(m['duration']).ljust(16)} | "
        f"{str(capacity).ljust(8)} | "
        f"{str(booked).ljust(6)} | "
        f"{_fmt_money(m['price']).rjust(11)} | "
        f"{_fmt_money(revenue).rjust(14)} | "
        f"{m['status'][:8].ljust(8)} |"
    )


def view_one():
    mid = input_int("กรอก Movie ID: ", 1)
    pairs = [(s, m) for (s, m) in _join_for_view_left() if m["movie_id"] == mid]
    if not pairs:
        print("ไม่พบข้อมูล"); return
    print(_header())
    for s, m in pairs:
        if s is not None and s["status"] != "Active":
            continue
        print(_render_row(s, m))
    print("----------------------------------------------------------------------------------------------------------------------------------------------------------------")
    pause()

def view_all():
    pairs = _join_for_view_left()
    pairs = [p for p in pairs if (p[0] is None) or (p[0]["status"] == "Active")]
    if not pairs:
        print("ไม่พบข้อมูล"); return
    print(_header())
    for s, m in pairs:
        print(_render_row(s, m))
    print("----------------------------------------------------------------------------------------------------------------------------------------------------------------")
    pause()

def filter_view():
    print("ตัวกรอง: 1) Status 2) Genre 3) Rating 4) Ticket price (<=)")
    from_choice = input_int("เลือก: ", 1, 4)
    pairs = _join_for_view_left()
    pairs = [p for p in pairs if (p[0] is None) or (p[0]["status"] == "Active")]
    if from_choice == 1:
        want = "Active" if input_str("กรอก Active/Deleted: ").lower().startswith("a") else "Deleted"
        pairs = [(s, m) for (s, m) in pairs if m["status"] == want]
    elif from_choice == 2:
        g = input_str("กรอก Genre: ").lower()
        pairs = [(s, m) for (s, m) in pairs if m["genre"].lower() == g]
    elif from_choice == 3:
        r = input_str("กรอก Rating: ").lower()
        pairs = [(s, m) for (s, m) in pairs if m["rating"].lower() == r]
    else:
        pmax = input_float("ราคาสูงสุด: ", 0)
        pairs = [(s, m) for (s, m) in pairs if m["price"] <= pmax]
    if not pairs:
        print("ไม่พบข้อมูล"); return
    print(_header())
    for s, m in pairs:
        print(_render_row(s, m))
    print("----------------------------------------------------------------------------------------------------------------------------------------------------------------")
    pause()

def summary_stats():
    pairs = _join_for_view_left()
    active_screens = [(s, m) for (s, m) in pairs if (s is not None and s["status"] == "Active")]
    total_scr   = len(active_screens)
    total_cap   = sum(s["capacity"] for s, _ in active_screens)
    total_booked= sum(s["booked"]   for s, _ in active_screens)
    total_rev   = sum(m["price"] * s["booked"] for s, m in active_screens)
    fill_rate   = (total_booked / total_cap * 100.0) if total_cap > 0 else 0.0
    movies        = read_movies()
    active_movies = [m for m in movies if m["status"] == "Active"]
    prices        = [m["price"] for m in active_movies]
    pmin = min(prices) if prices else 0.0
    pmax = max(prices) if prices else 0.0
    pavg = (sum(prices) / len(prices)) if prices else 0.0
    gcount = {}
    for m in active_movies:
        gcount[m["genre"]] = gcount.get(m["genre"], 0) + 1
    print("Summary")
    print(f"- Total Screenings : {total_scr}")
    print(f"- Total Capacity   : {total_cap}")
    print(f"- Total Booked     : {total_booked}")
    print(f"- Total Revenue    : {_fmt_money(total_rev)} THB")
    print(f"- Avg Fill Rate    : {fill_rate:.2f} %")
    print("")
    print("Ticket Price Statistics (Active only)")
    print(f"- Min : {pmin:.2f}")
    print(f"- Max : {pmax:.2f}")
    print(f"- Avg : {pavg:.2f}")
    print("")
    print("Movies by Genre (Active only)")
    for g, c in gcount.items():
        print(f"- {g}  : {c} เรื่อง")
    pause()

def generate_report():
    os.makedirs(REPORT_DIR, exist_ok=True)
    pairs_left       = _join_for_view_left()
    movies           = read_movies()
    active_movies    = [m for m in movies if m["status"] == "Active"]
    active_screens   = [(s, m) for (s, m) in pairs_left if (s is not None and s["status"] == "Active")]
    movies_no_screen = [m for (s, m) in pairs_left if s is None]
    total_scr    = len(active_screens)
    total_cap    = sum(s["capacity"] for s, _ in active_screens)
    total_booked = sum(s["booked"]   for s, _ in active_screens)
    total_rev    = sum(m["price"] * s["booked"] for s, m in active_screens)
    fill_rate    = (total_booked / total_cap * 100.0) if total_cap > 0 else 0.0
    prices = [m["price"] for m in active_movies]
    pmin = min(prices) if prices else 0.0
    pmax = max(prices) if prices else 0.0
    pavg = (sum(prices) / len(prices)) if prices else 0.0
    gcount = {}
    for m in active_movies:
        gcount[m["genre"]] = gcount.get(m["genre"], 0) + 1
    with open(REPORT_TXT, "w", encoding="utf-8") as r:
        r.write("Cinema Backend Report\n")
        r.write(f"Generated at: {now()}\n\n")
        r.write("Summary\n")
        r.write(f"- Total Movies      : {len(movies)}\n")
        r.write(f"- Active Movies     : {sum(1 for m in movies if m['status']=='Active')}\n")
        r.write(f"- Deleted Movies    : {sum(1 for m in movies if m['status']=='Deleted')}\n")
        r.write(f"- Total Screenings  : {total_scr}\n")
        r.write(f"- Total Capacity    : {total_cap}\n")
        r.write(f"- Total Booked      : {total_booked}\n")
        r.write(f"- Total Revenue     : {_fmt_money(total_rev)} THB\n")
        r.write(f"- Avg Fill Rate     : {fill_rate:.2f} %\n\n")
        r.write("Ticket Price Statistics (Active movies)\n")
        r.write(f"- Min : {pmin:.2f}\n")
        r.write(f"- Max : {pmax:.2f}\n")
        r.write(f"- Avg : {pavg:.2f}\n\n")
        r.write("Movies by Genre (Active movies)\n")
        if not gcount:
            r.write("- (none)\n\n")
        else:
            for g, c in gcount.items():
                r.write(f"- {g}  : {c} เรื่อง\n")
            r.write("\n")
        r.write("Table A — Active screenings\n")
        r.write(_header() + "\n")
        if not active_screens:
            r.write("(empty)\n")
        else:
            for s, m in active_screens:
                r.write(_render_row(s, m) + "\n")
        r.write("----------------------------------------------------------------------------------------------------------------------------------------------------------------\n\n")
    print(f"สร้างไฟล์ {REPORT_TXT} แล้ว")
    pause()