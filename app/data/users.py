from app.data.db import connect_database
import sqlite3

def get_user_by_username(username: str):
    """Retrieve user by username."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, password_hash, role, created_at FROM users WHERE username = ?",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()
    return user

def insert_user(username: str, password_hash: str, role: str = 'user'):
    """Insert a new user into the database."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role)
    )
    conn.commit()
    conn.close()
    return cursor.lastrowid

def update_user(username: str, password_hash: str = None, role: str = None):
    """Update user details."""
    conn = connect_database()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if password_hash:
        updates.append("password_hash = ?")
        params.append(password_hash)
    if role:
        updates.append("role = ?")
        params.append(role)
    if not updates:
        conn.close()
        return 0 #nothing to update
    
    #build final SQL query
    set_clause = ", ".join(updates)
    sql = f"UPDATE users SET {set_clause} WHERE username = ?"

    params.append(username)

    try:
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount
    except sqlite3.DatabaseError as e:
        print(f"Database error during update: {e}")
        return False
    finally:
        conn.close()

def delete_user(username: str):
    """Delete user by username."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM users WHERE username = ?",
        (username,)
    )
    conn.commit()
    rows_deleted = cursor.rowcount
    conn.close()
    return rows_deleted
