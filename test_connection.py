
import mysql.connector

db = mysql.connector.connect(
    host="127.0.0.1",
    user="student_app",
    password="StudentPass123!",
    database="student_performance",
    port=3306
)

if db.is_connected():
    print("SUCCESSFULLY CONNECTED TO MARIADB!")

db.close()

