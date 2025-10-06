from project import (
    add_movie, add_screening,
    update_movie, update_screening,
    delete_menu,
    view_one, view_all, filter_view, summary_stats,
    generate_report,
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

def print_menu():
    print("-----------------------------")
    print("1) Add (เพิ่ม)")
    print("2) Update (แก้ไข)")
    print("3) Delete (ลบ)")
    print("4) View (ดู)")
    print("5) Generate Report (.txt)")
    print("0) Exit (ออก)")
    print("-----------------------------")
    return input_int("เลือกเมนู: ", 0, 5)

def print_add_menu():
    print("-----------------------------")
    print("1) เพิ่มหนัง")
    print("2) เพิ่มรอบฉาย")
    print("0) Back")
    print("-----------------------------")
    return input_int("เลือกเมนู: ", 0, 2)

def print_update_menu():
    print("-----------------------------")
    print("1) แก้ไขข้อมูล Movie")
    print("2) แก้ไขข้อมูล Screening")
    print("0) Back")
    print("-----------------------------")
    return input_int("เลือกเมนู: ", 0, 2)

def print_view_menu():
    print("-----------------------------")
    print("1) View One")
    print("2) View All")
    print("3) Filter View")
    print("4) Summary Statistics")
    print("0) Back")
    print("-----------------------------")
    return input_int("เลือกเมนู: ", 0, 4)

def run_menu():
    while True:
        ch = print_menu()
        if ch == 0:
            print("ขอบคุณที่ใช้บริการ")
            break
        elif ch == 1:
            sub = print_add_menu()
            if sub == 1: add_movie()
            elif sub == 2: add_screening()
        elif ch == 2:
            sub = print_update_menu()
            if sub == 1: update_movie()
            elif sub == 2: update_screening()
        elif ch == 3:
            delete_menu()
        elif ch == 4:
            while True:
                vv = print_view_menu()
                if vv == 0: break
                elif vv == 1: view_one()
                elif vv == 2: view_all()
                elif vv == 3: filter_view()
                elif vv == 4: summary_stats()
        elif ch == 5:
            generate_report()

if __name__ == "__main__":
    try:
        run_menu()
    except KeyboardInterrupt:
        print("\nออกจากโปรแกรม")
