import mysql.connector

def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="inventory_system"
    )

# session.py
LOGGED_IN_EMPLOYEE_ID = None
LOGGED_IN_ROLE = None
LOGGED_IN_USER_INFO = None
