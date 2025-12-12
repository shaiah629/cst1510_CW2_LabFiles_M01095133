import sqlite3
import bcrypt
from pathlib import Path
from data.db import connect_database
DATA_DIR = Path("DATA")

def register_user(username, password, role='user'):
    """Register new user with password hashing."""
    conn = connect_database()
    cursor = conn.cursor()
    

    #check if user already exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, f"Username '{username}' already exists."

    #hash the password
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    password_hash = hashed.decode('utf-8')
    
    #insert new user
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role)
    )
    
    with open("DATA/users.txt", 'a') as file:
        file.write(f"{username},{password_hash},{role}\n")

    conn.commit()
    conn.close()
    
    return True, f"User '{username}' registered successfully!"

def login_user(username, password):
    """Authenticate user."""
    conn = connect_database()
    cursor = conn.cursor()
    
    #find user
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return False, "Username not found."
    
    #verify password (user[2] is password_hash column)
    stored_hash = user[2]
    password_bytes = password.encode('utf-8')
    hash_bytes = stored_hash.encode('utf-8')
    
    if bcrypt.checkpw(password_bytes, hash_bytes):
        return True, f"Welcome, {username}!"
    else:
        return False, "Invalid password."