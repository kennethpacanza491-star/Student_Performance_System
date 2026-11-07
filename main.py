
import mysql.connector
import re

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

except mysql.connector.Error as error:
    print("\nDATABASE CONNECTION ERROR:", error)
    raise SystemExit


# ==========================================
# CREATE STUDENT TABLE
# ==========================================

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


# ==========================================
# GRADE STATUS FUNCTION
# ==========================================

def calculate_status(average):

    if average >= 90:
        return "Outstanding"
    elif average >= 85:
        return "Very Satisfactory"
    elif average >= 80:
        return "Satisfactory"
    elif average >= 75:
        return "Passed"
    else:
        return "Failed"


def calculate_average(student):

    total = (
        float(student["preliminary_grade"])
        + float(student["midterm_grade"])
        + float(student["final_grade"])
    )

    return total / 3


# ==========================================
# SEARCH STUDENT FUNCTION
# ==========================================

def search_student(name):

    cursor.execute("""
        SELECT student_id, name, email,
           preliminary_grade, midterm_grade, final_grade
        FROM students
        WHERE LOWER(name) = LOWER(%s)
        """, (name,))
        
    return cursor.fetchone()


# ==========================================
# NAME VALIDATION
# ==========================================

def get_name():

    attempts = 0

    while attempts < 3:

        name = input("Enter name: ").strip()

        if not all(word.isalpha() for word in name.split()):
            print("\nNOTE: Letters only and nothing else.\n")

        elif len(name.split()) < 2:
            print("\nNOTE: Name must have 2 or more words.\n")

        elif not name.istitle():
            print("\nNOTE: Each word must start with a capital letter.\n")

        else:
            cursor.execute("""
            SELECT student_id FROM students
            WHERE LOWER(name) = LOWER(%s)
            """, (name,))

            if cursor.fetchone():
                print("\nNOTE: This name is already in use.\n")
            else:
                return name

        attempts += 1

    print("NOTE: Too many attempts. Returning to menu.\n")
    return None


# ==========================================
# EMAIL VALIDATION
# ==========================================

def get_email():

    attempts = 0

    while attempts < 3:

        email = input("Enter your email address: ").strip()

        if not email:
            print("\nERROR: Email address cannot be empty.\n")

        elif " " in email:
            print("\nERROR: Email must not contain spaces.\n")

        elif email.count("@") != 1:
            print("\nERROR: Email must contain exactly one '@'.\n")

        else:
            username, domain = email.split("@")

            if not username:
                print("\nERROR: Email username is required.\n")

            elif not domain:
                print("\nERROR: Email domain is required.\n")

            elif username.startswith(".") or username.endswith("."):
                print("\nERROR: Username cannot start or end with a dot.\n")

            elif ".." in username or ".." in domain:
                print("\nERROR: Consecutive dots are not allowed.\n")

            elif domain.startswith(".") or domain.endswith("."):
                print("\nERROR: Invalid domain format.\n")

            elif not re.fullmatch(
                r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
                r"@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*"
                r"\.[A-Za-z]{2,}",
                email
            ):
                print("\nERROR: Invalid email address.\n")

            else:
                domain_parts = domain.split(".")

                if any(
                    not part or
                    part.startswith("-") or
                    part.endswith("-")
                    for part in domain_parts
                ):
                    print("\nERROR: Invalid domain name.\n")

                else:
                    return email

        attempts += 1

    print("NOTE: Too many attempts. Returning to menu.\n")
    return None


# ==========================================
# GRADE VALIDATION
# ==========================================

def get_grade(label):

    attempts = 0

    while attempts < 3:

        grade = input(f"Enter {label} grade: ")

        try:
            grade = float(grade)

            if not 0 <= grade <= 100:
                print("\nNOTE: Grade must be between 0 and 100.\n")

            else:
                return grade

        except ValueError:
            print("\nNOTE: Numbers only.\n")

        attempts += 1

    print("NOTE: Too many attempts. Returning to menu.\n")
    return None


# ==========================================
# DISPLAY STUDENT INFORMATION
# ==========================================

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


# ==========================================
# MAIN MENU
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


    # ======================================
    # 1. ADD STUDENTS
    # ======================================

    if select == "1":

        try:
            enter = int(input("\nHow many students will be entered? "))

            if enter <= 0:
                print("\nNOTE: Enter a number greater than zero.\n")
                continue

        except ValueError:
            print("\nNOTE: Type the number only.\n")
            continue

        for i in range(enter):

            print(f"\nSTUDENT[{i + 1}]")

            name = get_name()

            if name is None:
                break

            email = get_email()

            if email is None:
                break

            preliminary_grade = get_grade("preliminary")

            if preliminary_grade is None:
                break

            midterm_grade = get_grade("midterm")

            if midterm_grade is None:
                break

            final_grade = get_grade("final")

            if final_grade is None:
                break

            try:

                cursor.execute("""
                INSERT INTO students
                (name, email, preliminary_grade,
                midterm_grade, final_grade)

                VALUES (%s, %s, %s, %s, %s)
                """, (
                    name,
                    email,
                    preliminary_grade,
                    midterm_grade,
                    final_grade
                ))

                db.commit()

                print("\n" + "=" * 65)
                print("STUDENT ADDED SUCCESSFULLY. ✅")
                print("=" * 65)

            except mysql.connector.Error as error:

                db.rollback()
                print("\nDATABASE ERROR:", error)


    # ======================================
    # 2. VIEW STUDENTS RECORD
    # ======================================

    elif select == "2":

        cursor.execute("SELECT * FROM students")
        records = cursor.fetchall()

        if not records:
            print("\nNOTE: NO STUDENT RECORDS TO DISPLAY YET.\n")
            continue

        print("\n" + "=" * 65)
        print("STUDENT RECORDS")
        print("=" * 65)

        print(f"{'ID':<6}{'Name':<25}{'Average':<15}{'Status':<20}")
        print("=" * 65)

        for student in records:

            average = calculate_average(student)
            status = calculate_status(average)

            print(
                f"{student['name']:<25}"
                f"{average:<15.2f}"
                f"{status:<20}"
            )

        print("=" * 65)


    # ======================================
    # 3. VIEW CLASS SUMMARY
    # ======================================

    elif select == "3":

        cursor.execute("SELECT * FROM students")
        records = cursor.fetchall()

        if not records:
            print("\nNOTE: NO STUDENT DATA TO SUMMARIZE YET.\n")
            continue

        averages = [
            calculate_average(student)
            for student in records
        ]

        highest_average = max(averages)
        lowest_average = min(averages)

        highest_index = averages.index(highest_average)
        lowest_index = averages.index(lowest_average)

        highest_student = records[highest_index]
        lowest_student = records[lowest_index]

        class_average = sum(averages) / len(averages)

        passed_students = sum(average >= 75 for average in averages)
        failed_students = sum(average < 75 for average in averages)

        passing_rate = (passed_students / len(records)) * 100

        print("\n" + "=" * 65)
        print("CLASS PERFORMANCE SUMMARY")
        print("=" * 65)

        print(
            f"Highest Average : {highest_student['name']} "
            f"- {highest_average:.2f}"
        )

        print(
            f"Lowest Average  : {lowest_student['name']} "
            f"- {lowest_average:.2f}"
        )

        print(f"\nClass Average   : {class_average:.2f}")
        print(f"\nPassed Students : {passed_students}")
        print(f"Failed Students : {failed_students}")
        print(f"Passing Rate    : {passing_rate:.2f}%")

        print("=" * 65)


    # ======================================
    # 4. SEARCH STUDENT
    # ======================================

    elif select == "4":
        cursor.execute("SELECT * FROM students")
        records = cursor.fetchall()
        if not records:
            print("\nNOTE: NO STUDENT DATA TO SEARCH YET.\n")
            continue
        attempts = 0

        while attempts < 3:

            search_name = input("\nEnter student name to search: ").strip()

            student = search_student(search_name)

            if student:

                display_student(student)
                break

            print("\nNOTE: STUDENT NOT FOUND.\n")
            attempts += 1

        if attempts >= 3:
            print("NOTE: Too many attempts. Returning to menu.\n")


    # ======================================
    # 5. EDIT STUDENT RECORD
    # ======================================

    elif select == "5":
        cursor.execute("SELECT * FROM students")
        records = cursor.fetchall()
        if not records:
            print("\nNOTE: NO STUDENT DATA TO EDIT YET.\n")
            continue

        attempts = 0
        found_student = None

        while attempts < 3:

            search_name = input("\nEnter student name to edit: ").strip()

            found_student = search_student(search_name)

            if found_student:
                break

            print("\nNOTE: STUDENT NOT FOUND.\n")
            attempts += 1

        if found_student is None:
            print("NOTE: Too many attempts. Returning to menu.\n")
            continue

        while True:

            print("\n" + "=" * 65)
            print("EDIT STUDENT RECORD")
            print("=" * 65)

            print("[1] Edit Name")
            print("[2] Edit Email")
            print("[3] Edit Preliminary Grade")
            print("[4] Edit Midterm Grade")
            print("[5] Edit Final Grade")
            print("[6] Back to Main Menu")

            choice = input("\nEnter choice: ").strip()

            if choice == "1":

                new_name = get_name(found_student['student_id'])

                if new_name is not None:

                    cursor.execute("""
                    UPDATE students
                    SET name = %s
                    WHERE student_id = %s
                    """, (
                        new_name,
                        found_student['student_id']
                    ))

                    db.commit()
                    print("\nSTUDENT NAME UPDATED SUCCESSFULLY. ✅")

            elif choice == "2":

                new_email = get_email()

                if new_email is not None:

                    cursor.execute("""
                    UPDATE students
                    SET email = %s
                    WHERE student_id = %s
                    """, (
                        new_email,
                        found_student["student_id"]
                    ))

                    db.commit()
                    print("\nSTUDENT EMAIL UPDATED SUCCESSFULLY. ✅")

            elif choice in ["3", "4", "5"]:

                if choice == "3":
                    column = "preliminary_grade"
                    label = "preliminary"

                elif choice == "4":
                    column = "midterm_grade"
                    label = "midterm"

                else:
                    column = "final_grade"
                    label = "final"

                new_grade = get_grade(label)

                if new_grade is not None:

                    # Column names are selected from the
                    # fixed choices above, not user input.

                    cursor.execute(
                        f"UPDATE students SET {column} = %s "
                        "WHERE student_id = %s",
                        (
                            new_grade,
                            found_student["student_id"]
                        )
                    )

                    db.commit()
                    print("\nSTUDENT GRADE UPDATED SUCCESSFULLY. ✅")

            elif choice == "6":
                print("\nReturning to main menu...\n")
                break

            else:
                print("\nNOTE: INVALID OPTION. CHOOSE AGAIN.\n")


    # ======================================
    # 6. DELETE STUDENT RECORD
    # ======================================

    elif select == "6":
        cursor.execute("SELECT * FROM students")
        records = cursor.fetchall()
        if not records:
            print("\nNOTE: NO STUDENT DATA TO DELETE YET.\n")
            continue

        attempts = 0
        found_student = None

        while attempts < 3:

            search_name = input("\nEnter student name to delete: ").strip()

            found_student = search_student(search_name)

            if found_student:
                break

            print("\nNOTE: STUDENT NOT FOUND.\n")
            attempts += 1

        if found_student is None:
            print("NOTE: Too many attempts. Returning to menu.\n")
            continue

        display_student(found_student)

        while True:

            confirm = input(
                "\nAre you sure you want to delete this student? (yes/no): "
            ).strip().lower()

            if confirm == "yes":

                cursor.execute("""
                DELETE FROM students
                WHERE student_id = %s
                """, (found_student["student_id"],))

                db.commit()

                print("\n" + "=" * 65)
                print("STUDENT RECORD DELETED SUCCESSFULLY. ✅")
                print("=" * 65)
                break

            elif confirm == "no":

                print("\nSTUDENT DELETION CANCELLED.\n")
                break

            else:
                print("\nNOTE: Please enter yes or no.\n")


    # ======================================
    # 7. EXIT
    # ======================================

    elif select == "7":

        print("\nEXITING STUDENT PERFORMANCE SYSTEM...")

        cursor.close()
        db.close()

        print("DATABASE CONNECTION CLOSED.")
        print("PROGRAM TERMINATED SUCCESSFULLY. ✅\n")

        break


    else:

        print("\nNOTE: NOTHING IN THE OPTION. CHOOSE AGAIN.\n")

