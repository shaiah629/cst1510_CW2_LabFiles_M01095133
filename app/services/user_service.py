import bcrypt
from pathlib import Path
from app.data.db import connect_database 
from app.data.users import get_user_by_username, insert_user

def register_user(username, password, role='user'):
    """Register new user with password hashing."""
    conn = connect_database()

    if get_user_by_username(username):
        conn.close()
        return False, f"Username '{username}' already exists."

    # Hash password
    password_hash = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    # Insert into database
    insert_user(username, password_hash, role)

    conn.close()
    return True, f"User '{username}' registered successfully."

def login_user(username, password):
    """Authenticate user."""
    user = get_user_by_username(username)
    if not user:
        return False, "User not found."
    
    # Verify password
    stored_hash = user[2]  # password_hash column
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        return True, f"Login successful!"
    return False, "Incorrect password."

def migrate_users_from_file(filepath='DATA/users.txt'):
    """Migrate users from text file to database."""
    # ensure filepath is a Path instance
    filepath = Path(filepath)

    if not filepath.exists():
        print(f"File not found: {filepath}. No users to migrate.")
        return 0

    # create a database connection
    conn = connect_database()
    try:
        cursor = conn.cursor()
        migrated_count = 0

        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Assuming format: username,password_hash,role (or just username,password_hash)
                parts = line.split(',')
                if len(parts) < 2:
                    print(f"Skipping invalid line in {filepath.name!r}: {line}")
                    continue

                username = parts[0]
                password_hash = parts[1]
                role = parts[2] if len(parts) > 2 else 'user'

                try:
                    # INSERT OR IGNORE skips the row if a UNIQUE constraint (username) is violated
                    cursor.execute(
                        "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                        (username, password_hash, role)
                    )
                    if cursor.rowcount > 0:
                        migrated_count += 1
                except Exception as e:
                    # Catch any unexpected errors during a single insert
                    print(f"Error migrating user {username}: {e}")

        conn.commit()
        print(f"Migrated {migrated_count} new users from {filepath.name}")
        return migrated_count
    finally:
        conn.close()