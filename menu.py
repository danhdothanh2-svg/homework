# main_with_role.py
# File mới - Menu phân quyền + Lưu/Tải file sinh viên (US13 + yêu cầu mới)
# Không sửa bất kỳ file cũ nào

import os
import csv
from auth import login, current_user
from student import StudentManager

ACCOUNTS_FILE = "accounts.json"
STUDENTS_FILE = "students.json"  # File gốc của dự án


def clear(): os.system('cls' if os.name == 'nt' else 'clear')


def load_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        import json
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def get_role(username):
    accounts = load_accounts()
    for acc in accounts:
        if acc["username"] == username:
            return acc.get("role", "student")
    return "student"


def change_password():
    if not current_user:
        print("Chưa đăng nhập!");
        input("Enter...");
        return

    import json
    accounts = load_accounts()
    username = current_user["username"]

    old = input("Mật khẩu cũ: ")
    user = next((a for a in accounts if a["username"] == username), None)
    if not user or user["password"] != old:
        print("Mật khẩu cũ sai!");
        input("Enter...");
        return

    new = input("Mật khẩu mới: ")
    confirm = input("Xác nhận: ")
    if new != confirm:
        print("Không khớp!");
        input("Enter...");
        return

    user["password"] = new
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=4, ensure_ascii=False)
    print("Đổi mật khẩu thành công!");
    input("Enter...")


# === Chức năng mới: Lưu và Tải file ===
def export_students_to_csv():
    manager = StudentManager()
    manager.load_students()  # Đảm bảo dữ liệu mới nhất
    students = manager.students

    if not students:
        print("Danh sách sinh viên trống!")
        input("Enter...")
        return

    filename = input("Nhập tên file để lưu (mặc định: students_export.csv): ").strip()
    if not filename:
        filename = "students_export.csv"
    if not filename.endswith(".csv"):
        filename += ".csv"

    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Mã SV", "Họ tên", "Ngày sinh", "Lớp", "Điểm TB"])
            for s in students:
                writer.writerow([s.student_id, s.name, s.dob, s.class_name, s.gpa])
        print(f"Đã lưu thành công vào {filename}!")
    except Exception as e:
        print(f"Lỗi khi lưu file: {e}")
    input("Enter...")


def import_students_from_csv():
    manager = StudentManager()
    filename = input("Nhập tên file CSV để tải: ").strip()
    if not os.path.exists(filename):
        print("File không tồn tại!")
        input("Enter...")
        return

    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # Bỏ qua header
            imported = 0
            for row in reader:
                if len(row) < 5:
                    continue
                student_id, name, dob, class_name, gpa = row[0].strip(), row[1].strip(), row[2].strip(), row[3].strip(), \
                row[4].strip()
                # Kiểm tra trùng mã SV
                if manager.find_student_by_id(student_id):
                    print(f"Bỏ qua: Mã SV {student_id} đã tồn tại.")
                    continue
                manager.add_student_manual(student_id, name, dob, class_name, gpa)
                imported += 1
            manager.save_students()  # Lưu vào students.json gốc
        print(f"Đã nhập thành công {imported} sinh viên!")
    except Exception as e:
        print(f"Lỗi khi đọc file: {e}")
    input("Enter...")


# === Menu sinh viên ===
def student_menu():
    manager = StudentManager()
    while True:
        clear()
        print("=== MENU SINH VIÊN ===")
        print("1. Xem thông tin cá nhân")
        print("2. Đổi mật khẩu")
        print("0. Đăng xuất")

        ch = input("\nChọn: ").strip()
        if ch == "1":
            sv = manager.find_student_by_id(current_user["username"])
            if sv:
                print(
                    f"\nMã SV: {sv.student_id}\nHọ tên: {sv.name}\nNgày sinh: {sv.dob}\nLớp: {sv.class_name}\nGPA: {sv.gpa}")
            else:
                print("Không tìm thấy thông tin.")
            input("\nEnter...")
        elif ch == "2":
            change_password()
        elif ch == "0":
            global current_user
            current_user = None
            print("Đăng xuất thành công!");
            input("Enter...")
            break


# === Menu giảng viên (có thêm 7,8,9) ===
def teacher_menu():
    manager = StudentManager()
    while True:
        clear()
        print("=== MENU GIẢNG VIÊN ===")
        print("1. Xem danh sách sinh viên")
        print("2. Thêm sinh viên")
        print("3. Sửa sinh viên")
        print("4. Xóa sinh viên")
        print("5. Tìm kiếm sinh viên")
        print("6. Xem thông tin cá nhân")
        print("7. Lưu danh sách sinh viên vào file")
        print("8. Tải danh sách sinh viên từ file")
        print("9. Cập nhật thông tin sinh viên")  # Gọi lại chức năng sửa
        print("0. Thoát")

        ch = input("\nChọn: ").strip()
        if ch == "1":
            manager.display_students()
        elif ch == "2":
            manager.add_student()
        elif ch == "3":
            manager.edit_student()
        elif ch == "4":
            manager.delete_student()
        elif ch == "5":
            manager.search_student()
        elif ch == "6":
            sv = manager.find_student_by_id(current_user["username"])
            if sv:
                print(
                    f"\nMã SV: {sv.student_id}\nHọ tên: {sv.name}\nNgày sinh: {sv.dob}\nLớp: {sv.class_name}\nGPA: {sv.gpa}")
            else:
                print("Giảng viên không có thông tin sinh viên.")
            input("\nEnter...")
        elif ch == "7":
            export_students_to_csv()
        elif ch == "8":
            import_students_from_csv()
        elif ch == "9":
            manager.edit_student()  # Cập nhật = sửa
        elif ch == "0":
            print("Tạm biệt!")
            return  # Thoát hẳn chương trình
        else:
            print("Lựa chọn không hợp lệ!");
            input("Enter...")


# === Main ===
def main():
    while True:
        clear()
        if current_user:
            role = get_role(current_user["username"])
            if role == "teacher":
                teacher_menu()
                break  # Khi chọn 0 ở teacher_menu sẽ thoát luôn
            else:
                student_menu()
        else:
            print("=== QUẢN LÝ SINH VIÊN ===")
            print("1. Đăng nhập")
            print("0. Thoát")
            ch = input("\nChọn: ").strip()
            if ch == "1":
                login()
            elif ch == "0":
                print("Tạm biệt!");
                break


if __name__ == "__main__":
    main()