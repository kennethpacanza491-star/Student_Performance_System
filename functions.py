import re
import mysql.connector

# ==========================================
# GRADE CALCULATIONS & STATUS
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
# DATABASE LOGIC
# ==========================================

def search_student(cursor, name):
    cursor.execute("""
        SELECT student_id, name, email,
           preliminary_grade, midterm_grade, final_grade
        FROM students
        WHERE LOWER(name) = LOWER(%s)
        """, (name,))
    return cursor.fetchone()

def add_student_db(cursor, db, name, email, p_grade, m_grade, f_grade):
    try:
        cursor.execute("""
        INSERT INTO students
        (name, email, preliminary_grade, midterm_grade, final_grade)
        VALUES (%s, %s, %s, %s, %s)
        """, (name, email, p_grade, m_grade, f_grade))
        db.commit()
        return True
    except mysql.connector.Error as error:
        db.rollback()
        print("\nDATABASE ERROR:", error)
        return False


# ==========================================
# INPUT VALIDATIONS
# ==========================================

def get_name(cursor, student_id=None):
    attempts = 0
    while attempts < 3:
        name = input("Enter name (or type 'cancel' to go back): ").strip()
        if name.lower() == 'cancel':
            return 'cancel'

        if not all(word.isalpha() for word in name.split()):
            print("\nNOTE: Letters only and nothing else.\n")
        elif len(name.split()) < 2:
            print("\nNOTE: Name must have 2 or more words.\n")
        elif not name.istitle():
            print("\nNOTE: Each word must start with a capital letter.\n")
        else:
            if student_id is not None:
                cursor.execute("""
                SELECT student_id FROM students
                WHERE LOWER(name) = LOWER(%s) AND student_id != %s
                """, (name, student_id))
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

def get_email():
    attempts = 0
    while attempts < 3:
        email = input("Enter email address (or type 'cancel' to go back): ").strip()
        if email.lower() == 'cancel':
            return 'cancel'

        if not email:
            print("\nERROR: Email address cannot be empty.\n")
        elif " " in email:
            print("\nERROR: Email must not contain spaces.\n")
        elif email.count("@") != 1:
            print("\nERROR: Email must contain exactly one '@'.\n")
        else:
            username, domain = email.split("@")
            if not username or not domain:
                print("\nERROR: Invalid email structure.\n")
            elif not re.fullmatch(
                r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
                r"@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*"
                r"\.[A-Za-z]{2,}", email
            ):
                print("\nERROR: Invalid email address.\n")
            else:
                return email
        attempts += 1

    print("NOTE: Too many attempts. Returning to menu.\n")
    return None

def get_grade(label):
    attempts = 0
    while attempts < 3:
        grade_input = input(f"Enter {label} grade (or type 'cancel' to go back): ").strip()
        if grade_input.lower() == 'cancel':
            return 'cancel'
        try:
            grade = float(grade_input)
            if not 0 <= grade <= 100:
                print("\nNOTE: Grade must be between 0 and 100.\n")
            else:
                return grade
        except ValueError:
            print("\nNOTE: Numbers only.\n")
        attempts += 1

    print("NOTE: Too many attempts. Returning to menu.\n")
    return None

