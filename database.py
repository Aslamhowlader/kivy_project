import mysql.connector
from mysql.connector import Error
import bcrypt

class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None
        try:
            # Connect to MySQL server first (no DB)
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",       # আপনার MySQL username
                password=""        # যদি password থাকে সেট দিন
            )
            self.cursor = self.conn.cursor()
            self.create_database()

            # Reconnect to citizen_portal database
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="citizen_portal"
            )
            self.cursor = self.conn.cursor(dictionary=True)
            print("✅ MySQL Database connected successfully!")

            # Ensure tables exist
            if self.conn and self.cursor:
                self.create_tables()

        except Error as e:
            print("❌ Error connecting to MySQL:", e)
            print("💡 Make sure MySQL server is running and credentials are correct.")

    def create_database(self):
        if not self.cursor:
            return
        try:
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS citizen_portal")
            print("✅ Database checked/created successfully.")
        except Error as e:
            print("❌ Database creation error:", e)

    def create_tables(self):
        if not self.cursor:
            return
        try:
            users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                phone VARCHAR(20),
                email VARCHAR(100),
                nid VARCHAR(50),
                username VARCHAR(100) UNIQUE,
                password VARCHAR(255),
                role ENUM('Citizen','Officer','Admin') DEFAULT 'Citizen'
            )
            """
            reports_table = """
            CREATE TABLE IF NOT EXISTS reports (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                problem_type VARCHAR(100),
                description TEXT,
                location VARCHAR(255),
                status ENUM('Pending','In Progress','Resolved') DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
            self.cursor.execute(users_table)
            self.cursor.execute(reports_table)
            self.conn.commit()
            print("✅ Tables created successfully.")
        except Error as e:
            print("❌ Table creation error:", e)

    def register_user(self, first, last, phone, email, nid, username, password, role='Citizen'):
        if not self.cursor:
            return False
        try:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            query = """
            INSERT INTO users (first_name, last_name, phone, email, nid, username, password, role)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """
            self.cursor.execute(query, (first, last, phone, email, nid, username, hashed, role))
            self.conn.commit()
            print(f"✅ User '{username}' registered successfully.")
            return True
        except Error as e:
            print("❌ Registration Error:", e)
            return False

    def login_user(self, username, password):
        if not self.cursor:
            return None
        try:
            query = "SELECT * FROM users WHERE username = %s"
            self.cursor.execute(query, (username,))
            user = self.cursor.fetchone()
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                print(f"✅ User '{username}' logged in successfully.")
                return user
            print("❌ Invalid username or password.")
            return None
        except Error as e:
            print("❌ Login Error:", e)
            return None

    def submit_report(self, user_id, problem_type, description, location):
        if not self.cursor:
            return False
        try:
            query = """
            INSERT INTO reports (user_id, problem_type, description, location)
            VALUES (%s,%s,%s,%s)
            """
            self.cursor.execute(query, (user_id, problem_type, description, location))
            self.conn.commit()
            print("✅ Report submitted successfully.")
            return True
        except Error as e:
            print("❌ Report Error:", e)
            return False

    def get_reports(self, user_id):
        if not self.cursor:
            return []
        try:
            query = """
            SELECT 
                id,
                problem_type,
                LEFT(description, 50) AS description_preview,
                location,
                status,
                created_at
            FROM reports 
            WHERE user_id = %s 
            ORDER BY created_at DESC
            """
            self.cursor.execute(query, (user_id,))
            return self.cursor.fetchall()
        except Error as e:
            print("❌ Fetch Reports Error:", e)
            return []

    def get_all_reports(self):
        """Get all reports for admin/officer view"""
        if not self.cursor:
            return []
        try:
            query = """
            SELECT 
                r.id,
                u.username,
                r.problem_type,
                LEFT(r.description, 50) AS description_preview,
                r.location,
                r.status,
                r.created_at
            FROM reports r
            JOIN users u ON r.user_id = u.id
            ORDER BY r.created_at DESC
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print("❌ Fetch All Reports Error:", e)
            return []
