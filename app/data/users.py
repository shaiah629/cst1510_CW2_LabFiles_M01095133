from app.data.db import connect_database
from pathlib import Path
import sqlite3
DATA_DIR = Path("app/data")

def get_user_by_username(username: str):
    """Retrieve user by username."""
    conn = connect_database()
    cursor = conn.cursor()
    
    #secure parameterized query
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
    
    #secure parameterized query
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role)
    )
    conn.commit()
    conn.close()
    return cursor.lastrowid

def migrate_users_from_file(filepath=DATA_DIR / "users.txt"):
    """Migrate users from text file to database using INSERT OR IGNORE."""
    conn = connect_database()
    
    if not filepath.exists():
        print(f"  - ⚠️ File not found: {filepath}. No users to migrate.")
        conn.close()
        return 0
    
    cursor = conn.cursor()
    migrated_count = 0
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            parts = line.split(',')
            if len(parts) < 2:
                username = parts[0]
                password_hash = parts[1]
                role = parts[2] if len(parts) > 2 else 'user'
                
                #INSERT OR IGNORE prevents failure if user already exists
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                        (username, password_hash, role)
                     )
                    if cursor.rowcount > 0:
                        migrated_count += 1
                except sqlite3.DatabaseError as e:
                    print(f"  - ❌ Database error for user '{username}': {e}")
            

    conn.commit()

conn = connect_database()
cursor = conn.cursor()
    
#query all users
cursor.execute("SELECT id, username, role FROM users")
users = cursor.fetchall()

print(" Users in database:")
print(f"{'ID':<5} {'Username':<15} {'Role':<10}")
print("-" * 35)
for user in users:
    print(f"{user[0]:<5} {user[1]:<15} {user[2]:<10}")

print(f"\nTotal users: {len(users)}")
conn.close()


