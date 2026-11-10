import mysql.connector
from authentication import authenticate
from functions import (
    calculate_average, calculate_status, search_student,
    add_student_db, get_name, get_email, get_grade
)

# ==========================================
# DATABASE CONNECTION
# ==========================================

try:
    db = mysql.connector.connect(
        host="127.0.0.1",
        user="student_app",
        password="StudentPass123!",
        database="student_performance",
        port=3306
    )
    cursor = db.cursor(dictionary=True)
    print("\nDATABASE CONNECTED SUCCESSFULLY. ✅")

    if not authenticate(db, cursor):
        cursor.close()
        db.close()
        print("\nDATABASE CONNECTION CLOSED.")
        raise SystemExit

except mysql.connector.Error as error:
    print("\nDATABASE CONNECTION ERROR:", error)
    raise SystemExit

# Create Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL,
    preliminary_grade DECIMAL(5,2) NOT NULL,
    midterm_grade DECIMAL(5,2) NOT NULL,
    final_grade DECIMAL(5,2) NOT NULL
)
""")
db.commit()

def display_student(student):
    average = calculate_average(student)
    status = calculate_status(average)
    print("\n" + "=" * 65)
    print("STUDENT INFORMATION")
    print("=" * 65)
    print(f"Student ID: {student['student_id']}")
    print(f"Name: {student['name']}")
    print(f"Email: {student['email']}")
    print(f"Preliminary Grade: {float(student['preliminary_grade']):.2f}")
    print(f"Midterm Grade: {float(student['midterm_grade']):.2f}")
    print(f"Final Grade: {float(student['final_grade']):.2f}")
    print(f"Average: {average:.2f}")
    print(f"Status: {status}")
    print("=" * 65)

def modify_student_record(found_student):
    while True:
        print("\n" + "=" * 65)
        print(f"EDIT RECORD FOR: {found_student['name']}")
        print("=" * 65)
        print("[1] Edit Name")
        print("[2] Edit Email")
        print("[3] Edit Preliminary Grade")
        print("[4] Edit Midterm Grade")
        print("[5] Edit Final Grade")
        print("[6] Finish / Return")

        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            new_name = get_name(cursor, found_student['student_id'])
            if new_name and new_name != 'cancel':
                cursor.execute("UPDATE students SET name = %s WHERE student_id = %s", (new_name, found_student['student_id']))
                db.commit()
                found_student['name'] = new_name
                print("\nSTUDENT NAME UPDATED SUCCESSFULLY. ✅")
        elif choice == "2":
            new_email = get_email()
            if new_email and new_email != 'cancel':
                cursor.execute("UPDATE students SET email = %s WHERE student_id = %s", (new_email, found_student["student_id"]))
                db.commit()
                found_student['email'] = new_email
                print("\nSTUDENT EMAIL UPDATED SUCCESSFULLY. ✅")
        elif choice in ["3", "4", "5"]:
            col_map = {"3": ("preliminary_grade", "preliminary"), "4": ("midterm_grade", "midterm"), "5": ("final_grade", "final")}
            col, label = col_map[choice]
            new_grade = get_grade(label)
            if new_grade and new_grade != 'cancel':
                cursor.execute(f"UPDATE students SET {col} = %s WHERE student_id = %s", (new_grade, found_student["student_id"]))
                db.commit()
                found_student[col] = new_grade
                print("\nSTUDENT GRADE UPDATED SUCCESSFULLY. ✅")
        elif choice == "6":
            break


# ==========================================
# MAIN LOOP
# ==========================================

while True:
    print("\n" + "=" * 65)
    print("STUDENT PERFORMANCE SYSTEM")
    print("=" * 65)
    print("\n[1] Add Students")
    print("[2] View Students Record")
    print("[3] View Class Summary")
    print("[4] Search Student")
    print("[5] Edit Student Record")
    print("[6] Delete Student Record")
    print("[7] Exit")
    print("\n" + "=" * 65)

    select = input("Enter choice: ").strip()
    print("=" * 65)

    if select == "1":
        try:
            enter_input = input("\nHow many students will be entered? (or 'cancel'): ").strip()
            if enter_input.lower() == 'cancel':
                continue
            enter = int(enter_input)
            if enter <= 0:
                continue
        except ValueError:
            print("\nNOTE: Type numbers only.\n")
            continue

        for i in range(enter):
            print(f"\nSTUDENT[{i + 1}]")
            name = get_name(cursor)
            if name in [None, 'cancel']: break
            email = get_email()
            if email in [None, 'cancel']: break
            p_grade = get_grade("preliminary")
            if p_grade in [None, 'cancel']: break
            m_grade = get_grade("midterm")
            if m_grade in [None, 'cancel']: break
            f_grade = get_grade("final")
            if f_grade in [None, 'cancel']: break

            if add_student_db(cursor, db, name, email, p_grade, m_grade, f_grade):
                print("\nSTUDENT ADDED SUCCESSFULLY. ✅")

    elif select == "2":
        cursor.execute("SELECT * FROM students")
        records = cursor.fetchall()
        if not records:
            print("\nNOTE: NO RECORDS YET.\n")
            continue
        print("\n" + "=" * 65)
        print(f"{'ID':<6}{'Name':<25}{'Average':<15}{'Status':<20}")
        print("=" * 65)
        for s in records:
            avg = calculate_average(s)
            print(f"{s['student_id']:<6}{s['name']:<25}{avg:<15.2f}{calculate_status(avg):<20}")
        print("=" * 65)

    elif select == "3":
        cursor.execute("SELECT * FROM students")
        records = cursor.fetchall()
        if not records:
            print("\nNOTE: NO DATA YET.\n")
            continue
        avgs = [calculate_average(s) for s in records]
        high, low = max(avgs), min(avgs)
        print("\n" + "=" * 65)
        print(f"Highest Avg : {records[avgs.index(high)]['name']} - {high:.2f}")
        print(f"Lowest Avg  : {records[avgs.index(low)]['name']} - {low:.2f}")
        print(f"Class Avg   : {sum(avgs)/len(avgs):.2f}")
        print("=" * 65)

    elif select == "4":
        cursor.execute("SELECT * FROM students")
        if not cursor.fetchall():
            print("\nNOTE: NO DATA YET.\n")
            continue
        while True:
            print("\n[1] Search Single\n[2] Search Multiple\n[3] Back")
            ch = input("Enter choice: ").strip()
            if ch == "1":
                name = input("Name to search: ").strip()
                s = search_student(cursor, name)
                if s: display_student(s)
                else: print("\nNOT FOUND.\n")
            elif ch == "2":
                name = input("Name (or 'done'): ").strip()
                if name.lower() == 'done': break
                s = search_student(cursor, name)
                if s: display_student(s)
                else: print("\nNOT FOUND.\n")
            elif ch == "3": break

    elif select == "5":
        cursor.execute("SELECT * FROM students")
        if not cursor.fetchall():
            print("\nNOTE: NO DATA YET.\n")
            continue
        while True:
            print("\n[1] Edit Single\n[2] Edit Multiple\n[3] Back")
            ch = input("Enter choice: ").strip()
            if ch == "1":
                s = search_student(cursor, input("Name to edit: ").strip())
                if s: modify_student_record(s)
                else: print("\nNOT FOUND.\n")
            elif ch == "2":
                name = input("Name to edit (or 'done'): ").strip()
                if name.lower() == 'done': break
                s = search_student(cursor, name)
                if s: modify_student_record(s)
                else: print("\nNOT FOUND.\n")
            elif ch == "3": break

    elif select == "6":
        cursor.execute("SELECT * FROM students")
        if not cursor.fetchall():
            print("\nNOTE: NO DATA YET.\n")
            continue
        while True:
            print("\n[1] Delete Single\n[2] Delete Multiple\n[3] Delete All\n[4] Back")
            ch = input("Enter choice: ").strip()
            if ch == "1":
                s = search_student(cursor, input("Name to delete: ").strip())
                if s and input("Confirm (yes/no): ").lower() == 'yes':
                    cursor.execute("DELETE FROM students WHERE student_id = %s", (s["student_id"],))
                    db.commit()
                    print("\nDELETED SUCCESSFULLY. ✅")
            elif ch == "2":
                ids = []
                while True:
                    name = input("Name to delete (or 'done'): ").strip()
                    if name.lower() == 'done': break
                    s = search_student(cursor, name)
                    if s and s['student_id'] not in ids: ids.append(s['student_id'])
                if ids and input("Confirm batch delete (yes/no): ").lower() == 'yes':
                    cursor.execute(f"DELETE FROM students WHERE student_id IN ({','.join(['%s']*len(ids))})", tuple(ids))
                    db.commit()
                    print("\nDELETED SUCCESSFULLY. ✅")
            elif ch == "3":
                if input("WARNING: Delete ALL? (yes/no): ").lower() == 'yes':
                    cursor.execute("DELETE FROM students")
                    db.commit()
                    print("\nALL DELETED. ✅")
            elif ch == "4": break

    elif select == "7" or (select.isdigit() and int(select) == 7):
        print("\nEXITING...")
        cursor.close()
        db.close()
        break

