import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv, dotenv_values

# Load the key for environment variables
load_dotenv()

# Replace the values in the dictionary below with your own database credentials
db_config = {
    "host": "localhost",
    "user": os.getenv('SQL_USER'),
    "password": os.getenv('SQL_PASSWORD'),
    "database": os.getenv('SQL_DATABASE')
}

# Check whether username exists in the database
def check_username_exists(username):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Replace 'users' with the name of the table containing the usernames
        query = "SELECT username FROM users WHERE username = %s"
        cursor.execute(query, (username,))

        result = cursor.fetchall()
        if len(result) == 1:
            return True
        return False

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Check whether email exists in the database
def check_email_exists(email):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Replace 'users' with the name of the table containing the emails
        query = "SELECT email FROM users WHERE email = %s"
        cursor.execute(query, (email,))

        result = cursor.fetchall()
        if len(result) == 1:
            return True
        return False

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Add user information to the database
def add_user(username, password, email):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Replace 'users' with the name of the table containing the usernames, passwords, and emails
        query = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, password, email))

        conn.commit()
        return True

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Get user id from the username
def get_id(username):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Replace 'users' with the name of the table containing the usernames and ids
        query = "SELECT id FROM users WHERE username = %s"
        cursor.execute(query, (username,))

        result = cursor.fetchall()
        if len(result) == 1:
            return result[0][0]
        return None

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Get username from user id
def get_username(user_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Replace 'users' with the name of the table containing the usernames and ids
        query = "SELECT username FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))

        result = cursor.fetchall()
        if len(result) == 1:
            return result[0][0]
        return None

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Get email from user id
def get_email(user_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Replace 'users' with the name of the table containing the emails and ids
        query = "SELECT email FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))

        result = cursor.fetchall()
        if len(result) == 1:
            return result[0][0]
        return None

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Save verification code and expiration time to the database
def save_verification_code(email, verification_code, expiration_time):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Replace 'verification_codes' with the name of the table containing the verification codes, expiration times, and emails
        query = "INSERT INTO email_verification (email, verification_code, expiration_time, email_verified) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (email, verification_code, expiration_time, 0))

        conn.commit()
        return True

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Get verification code and expiration time from email
def get_verification_code_expiration_time(email):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Replace 'email_verification' with the name of the table containing the verification codes, expiration times, and emails
        query = "SELECT verification_code, expiration_time FROM email_verification WHERE email = %s ORDER BY expiration_time DESC LIMIT 1"
        cursor.execute(query, (email,))
        row = cursor.fetchone()

        if row:
            verification_code, expiration_time = row
            return verification_code, expiration_time

        return None, None

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None, None

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Mark email as verified
def mark_email_as_verified(user_email):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Replace 'users' with the name of the table containing the emails and ids
        query = "UPDATE users SET email_verify = 1 WHERE email = %s"
        cursor.execute(query, (user_email,))

        conn.commit()
        return True

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Delete the verification email from the email_verification table
def delete_email():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Replace 'email_verification' with the name of the table containing the verification codes, expiration times, and emails
        query = "DELETE FROM email_verification WHERE expiration_time < %s"
        cursor.execute(query, (datetime.now(),))

        conn.commit()
        return True

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Delete user from database
def delete_user(user_email):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Replace 'users' with the name of the table containing the usernames, passwords, and emails
        query = "DELETE FROM users WHERE email = %s"
        cursor.execute(query, (user_email,))

        conn.commit()
        return True

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_unverified_users():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)  # Use dictionary cursor to return rows as dictionaries

        # Replace 'users' with the name of the table containing the usernames, passwords, and emails
        query = "SELECT * FROM users WHERE email_verify = 0"
        cursor.execute(query)
        rows = cursor.fetchall()

        return rows

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def check_email_verified(username):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Replace 'users' with the name of the table containing the usernames, passwords, and emails
        query = "SELECT email_verify FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        row = cursor.fetchone()

        if row:
            return row[0]

        return None

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_hashed_password(username):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Replace 'users' with the name of the table containing the usernames, passwords, and emails
        query = "SELECT password FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        row = cursor.fetchone()

        if row:
            return row[0]

        return None

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
def update_password(id, password):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Replace 'users' with the name of the table containing the usernames, passwords, and emails
        query = "UPDATE users SET password = %s WHERE id = %s"
        cursor.execute(query, (password, id))

        conn.commit()
        return True

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()