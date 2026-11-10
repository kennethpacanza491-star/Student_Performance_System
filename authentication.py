
import re
import hashlib
import secrets
from getpass import getpass


# ==========================================
# CREATE AUTHENTICATION TABLE
# ==========================================

def create_authentication_table(cursor, db):

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        password_salt VARCHAR(255) NOT NULL
    )
    """)

    db.commit()


# ==========================================
# PASSWORD HASHING FUNCTION
# ==========================================

def hash_password(password, salt):

    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        600000
    ).hex()


# ==========================================
# ACCOUNT NAME VALIDATION
# ==========================================

def get_account_name(cursor):

    attempts = 0

    while attempts < 3:

        name = input("Enter your name: ").strip()

        if not all(word.isalpha() for word in name.split()):

            print("\nNOTE: Letters only and nothing else.\n")

        elif len(name.split()) < 2:

            print("\nNOTE: Name must have 2 or more words.\n")

        elif not name.istitle():

            print("\nNOTE: Each word must start with a capital letter.\n")

        else:

            cursor.execute("""
            SELECT user_id FROM system_users
            WHERE LOWER(name) = LOWER(%s)
            """, (name,))

            if cursor.fetchone():

                print("\nNOTE: This account name is already registered.\n")

            else:

                return name

        attempts += 1

    print("\nNOTE: Too many attempts. Returning to menu.\n")

    return None


# ==========================================
# PASSWORD VALIDATION
# ==========================================

def validate_password(password):

    if len(password) < 8:

        return "Password must contain at least 8 characters."

    elif not re.search(r"[A-Z]", password):

        return "Password must contain at least one uppercase letter."

    elif not re.search(r"[a-z]", password):

        return "Password must contain at least one lowercase letter."

    elif not re.search(r"[0-9]", password):

        return "Password must contain at least one number."

    elif not re.search(r"[^A-Za-z0-9\s]", password):

        return "Password must contain at least one special character."

    elif re.search(r"\s", password):

        return "Password must not contain spaces."

    return None


# ==========================================
# ACCOUNT REGISTRATION
# ==========================================

def register_account(cursor, db):

    print("\n" + "=" * 65)
    print("SYSTEM ACCOUNT REGISTRATION")
    print("=" * 65)

    print("\nCREATE YOUR ADMINISTRATOR ACCOUNT.\n")

    name = get_account_name(cursor)

    if name is None:

        return False

    attempts = 0

    while attempts < 3:

        password = getpass("Create password: ")

        error = validate_password(password)

        if error:

            print("\nERROR:", error, "\n")

        else:

            confirm_password = getpass("Confirm password: ")

            if password != confirm_password:

                print("\nERROR: Passwords do not match.\n")

            else:

                salt = secrets.token_bytes(32)

                password_hash = hash_password(password, salt)

                cursor.execute("""
                INSERT INTO system_users
                (name, password_hash, password_salt)
                VALUES (%s, %s, %s)
                """, (
                    name,
                    password_hash,
                    salt.hex()
                ))

                db.commit()

                print("\n" + "=" * 65)
                print("ACCOUNT REGISTERED SUCCESSFULLY. ✅")
                print("=" * 65)

                return True

        attempts += 1

    print("\nNOTE: Too many attempts. Registration cancelled.\n")

    return False


# ==========================================
# ACCOUNT LOGIN
# ==========================================

def login_account(cursor):

    print("\n" + "=" * 65)
    print("STUDENT PERFORMANCE SYSTEM LOGIN")
    print("=" * 65)

    attempts = 0

    while attempts < 3:

        name = input("\nEnter your name: ").strip()

        password = getpass("Enter your password: ")

        cursor.execute("""
        SELECT name, password_hash, password_salt
        FROM system_users
        WHERE LOWER(name) = LOWER(%s)
        """, (name,))

        account = cursor.fetchone()

        if account:

            salt = bytes.fromhex(account["password_salt"])

            entered_hash = hash_password(password, salt)

            if secrets.compare_digest(
                entered_hash,
                account["password_hash"]
            ):

                print("\n" + "=" * 65)
                print(
                    "LOGIN SUCCESSFUL. WELCOME,",
                    account["name"].upper() + "!"
                )
                print("=" * 65)

                return True

        print("\nERROR: Incorrect name or password.\n")

        attempts += 1

    print("\nNOTE: Too many login attempts. Access denied.\n")

    return False


# ==========================================
# AUTHENTICATION CONTROL
# ==========================================

def authenticate(db, cursor):

    create_authentication_table(cursor, db)

    cursor.execute("""
    SELECT COUNT(*) AS total
    FROM system_users
    """)

    account_count = cursor.fetchone()["total"]

    if account_count == 0:

        return register_account(cursor, db)

    else:

        return login_account(cursor)

