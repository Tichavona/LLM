import pyodbc
from werkzeug.security import generate_password_hash, check_password_hash
import random
import smtplib
from email.mime.text import MIMEText
import streamlit as st

class UserAuth:
    def __init__(self, db_conn_str):
        self.db_conn_str = db_conn_str
        self._create_users_table()

    def get_user_id(self, email):
        conn = pyodbc.connect(self.db_conn_str)
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
        conn = pyodbc.connect(self.db_conn_str)
        cursor = conn.cursor()
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
            CREATE TABLE users (
                id INT IDENTITY(1,1) PRIMARY KEY,
                email NVARCHAR(255) UNIQUE NOT NULL,
                first_name NVARCHAR(100) NOT NULL,
                surname NVARCHAR(100) NOT NULL,
                mobile_number NVARCHAR(20) NOT NULL,
                account_number NVARCHAR(50),
                department NVARCHAR(100),
                profession NVARCHAR(100),
                password_hash NVARCHAR(255) NOT NULL,
                user_type NVARCHAR(50)
            )
        ''')
        conn.commit()
        conn.close()

    def register_user(self, email, password, first_name, surname, mobile_number, account_number=None, 
                      department=None, profession=None, user_type="Staff"):
        password_hash = generate_password_hash(password)
        conn = pyodbc.connect(self.db_conn_str)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (email, first_name, surname, mobile_number, account_number, department, profession, password_hash, user_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (email, first_name, surname, mobile_number, account_number, department, profession, password_hash, user_type))
            conn.commit()
        except pyodbc.IntegrityError as e:
            print(f"Registration failed: {e}")
            return False  # Email already registered
        finally:
            cursor.close()
            conn.close()
        return True
    
    def login_user(self, email, password):
        conn = pyodbc.connect(self.db_conn_str)
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
        conn = pyodbc.connect(self.db_conn_str)
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
        conn = pyodbc.connect(self.db_conn_str)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users
            SET password_hash=?
            WHERE email=?
        ''', (password_hash, email))
        conn.commit()
        cursor.close()
        conn.close()
