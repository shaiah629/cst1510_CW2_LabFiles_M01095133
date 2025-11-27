import bcrypt
from pathlib import Path
from app.data.db import connect_database, DATA_DIR
from app.data.users import get_user_by_username, insert_user
DATA_DIR = Path("app/data")

def register_user(username: str, password: str, role: str = 'user'):
    """Register new user with password hashing."""
    conn = connect_database() 
    
    #check if user already exists
    if get_user_by_username(username):
        conn.close()
        return False, f"Username '{username}' already exists."

    #hash password
    password_hash = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    #insert into database
    insert_user(username, password_hash, role)
    
    conn.close()
    return True, f"User '{username}' registered successfully."

def login_user(username: str, password: str):
    """Authenticate user."""
    user = get_user_by_username(username)
    
    if not user:
        return False, "User not found."
    
    #verify password
    #user[2] is the password_hash column returned by get_user_by_username
    stored_hash = user[2] 
    
    try:
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            return True, f"Login successful! Role: {user[3]}"
        return False, "Incorrect password."
    except ValueError:
        return False, "Error validating password hash."

def migrate_users_from_file(filepath=DATA_DIR / "users.txt"):
    """Migrate users from text file to database using INSERT OR IGNORE."""
    conn = connect_database()
    
    if not filepath.exists():
        print(f"  - ⚠️ File not found: {filepath}. No users to migrate.")
        conn.close()
        return 0
    
    cursor = conn.cursor()
    migrated_count = 0
    
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split(',')
                if len(parts) < 2: continue

                username = parts[0]
                password_hash = parts[1]
                role = parts[2] if len(parts) > 2 else 'user'
                
                #INSERT OR IGNORE prevents failure if user already exists
                cursor.execute(
                    "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (username, password_hash, role)
                )
                if cursor.rowcount > 0:
                    migrated_count += 1

        conn.commit()
        print(f"  - ✅ Migrated {migrated_count} new users from {filepath.name}")
        return migrated_count
    except Exception as e:
        print(f"  - ❌ Error during user migration: {e}")
        return 0
    finally:
        conn.close()