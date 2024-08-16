import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import random
import smtplib
from email.mime.text import MIMEText
import streamlit as st

class UserAuth:
    def __init__(self, db_file):
        self.db_file = db_file
        self._create_users_table()
        self._create_user_location_data_table()
        self._create_chat_sessions_table()
        self._create_chat_activity_table()

    def get_user_id(self, email):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return result[0]  # Assuming the id column is the first column returned
        else:
            return None

    def _create_users_table(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                surname TEXT NOT NULL,
                mobile_number TEXT NOT NULL,
                account_number TEXT,
                department TEXT,
                profession TEXT,
                password_hash TEXT NOT NULL,
                user_type TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def _create_user_location_data_table(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS UserLocationData (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                status TEXT,
                event_time TEXT,
                geolocation_coordinates TEXT,
                ip_address TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()
        conn.close()

    def _create_chat_sessions_table(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ChatSessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                chat_name TEXT NOT NULL,
                chat_data TEXT NOT NULL,
                created_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()
        conn.close()

    def _create_chat_activity_table(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ChatActivity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                chat_name TEXT NOT NULL,
                user_input TEXT NOT NULL,
                llm_response TEXT NOT NULL,
                created_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()
        conn.close()

    def register_user(self, email, password, first_name, surname, mobile_number, account_number=None, 
                      department=None, profession=None, user_type="Staff"):
        password_hash = generate_password_hash(password)
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (email, first_name, surname, mobile_number, account_number, department, profession, password_hash, user_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (email, first_name, surname, mobile_number, account_number, department, profession, password_hash, user_type))
            conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"Registration failed: {e}")
            return False  # Email already registered
        finally:
            cursor.close()
            conn.close()
        return True
    
    def login_user(self, email, password):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT id, password_hash FROM users WHERE email=?', (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user[1], password):
            # Store user ID and email in Streamlit session state
            st.session_state['user_id'] = user[0]
            st.session_state['email'] = email
            return user[0]  # Return the user_id
        return False

    def send_reset_code(self, email):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email=?', (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            return None

        reset_code = str(random.randint(100000, 999999))

        # Send reset code via email
        self._send_email(email, "Password Reset Code", f"Your reset code is {reset_code}")

        return reset_code

    def _send_email(self, to_email, subject, body):
        sender_email = "your-email@example.com"  # Replace with your email
        sender_password = "your-email-password"  # Replace with your email password

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email

        with smtplib.SMTP_SSL("smtp.example.com", 465) as server:  # Replace with your SMTP server details
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())

    def update_password(self, email, new_password):
        password_hash = generate_password_hash(new_password)
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users
            SET password_hash=?
            WHERE email=?
        ''', (password_hash, email))
        conn.commit()
        cursor.close()
        conn.close()
