import bcrypt
import os

USER_DATA_FILE = 'users.txt'

def hash_password(plain_text_password):
    #encode password to bytes
    password_bytes = plain_text_password.encode('utf-8')
    #generate a salt
    salt = bcrypt.gensalt()
    #hash password
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    #decode hash back to string
    return hashed_password.decode('utf-8')

def verify_password(plain_text_password, hashed_password):
    #encode to bytes
    password_bytes = plain_text_password.encode('utf-8')    
    #generate a salt
    hashed_password_bytes = hashed_password.encode('utf-8')  
    #decode hash back to string
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)

def register_user(username, password):
    #check if the username already exists
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            for line in file:
                stored_username = line.strip().split(",")[0]
                if stored_username == username:
                    return False #username already exists
                
    #hash password
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

    #append new user to file
    with open(USER_DATA_FILE, 'a') as file:
        file.write(f"{username},{hashed_password}\n")
    
    print("DEBUG: Registration succeeded")
    return True

def user_exist(username):
    #handle case where file doesn't exist
    if not os.path.exists(USER_DATA_FILE):
        return False
    
    #read each file and check for username
    with open(USER_DATA_FILE, 'r') as file:
        for line in file:
            stored_username = line.strip().split(",")[0]
            if stored_username == username:
                return True
    return False

def login_user(username, password):
    #handle case where no users are registered yet
    if not os.path.exists(USER_DATA_FILE):
        return False #no users stored yet
    
    #search for username in the file
    with open(USER_DATA_FILE, 'r') as file:
        for line in file:
            stored_username, stored_hash = line.strip().split(",")
            if stored_username == username:
                password_bytes = password.encode('utf-8')
                stored_hash_bytes = stored_hash.encode('utf-8')
                return bcrypt.checkpw(password_bytes, stored_hash_bytes)
    return False #username not found

def validate_username(username):
    if not username:
        return False, "Username cannot be empty"
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    return True, "" #if valid

def validate_password(password):
    if not password:
        return False, "Password cannot be empty"
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit"
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter"
    return True, "" #if valid

def display_menu():
    """Displays the main menu options."""
    print("\n" + "="*50)
    print(" MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print(" Secure Authentication System")
    print("="*50)
    print("\n[1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-"*50)

def main():
    """Main program loop."""
    print("\nWelcome to the Week 7 Authentication System!")

    while True:
        display_menu()
        choice = input("\nPlease select an option (1-3): ").strip()

        if choice == '1':
            # Registration flow
            print("\n--- USER REGISTRATION ---")
            username = input("Enter a username: ").strip()

            # Validate username
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            password = input("Enter a password: ").strip()

            # Validate password
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            # Confirm password
            password_confirm = input("Confirm password: ").strip()
            if password != password_confirm:
                print("Error: Passwords do not match.")
                continue

            # Register the user
            if register_user(username, password):
                print(f"\nSuccess: User '{username}' registered successfully!")
            else:
                print(f"\nError: Username '{username}' already exists.")


        elif choice == '2':
            # Login flow
            print("\n--- USER LOGIN ---")
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()

            # Attempt login
            if login_user(username, password):
                print(f"\nSuccess: Welcome, {username}!")
            elif user_exist(username):
                print("\nError: Invalid password.")
            elif not user_exist(username):
                print("\nError: Username not found.")
            else:
                # Optional: Ask if they want to logout or exit
                input("\nPress Enter to return to main menu...")

        elif choice == '3':
            # Exit
            print("\nThank you for using the authentication system.")
            print("Exiting...")
            break

        else:
            print("\nError: Invalid option. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()