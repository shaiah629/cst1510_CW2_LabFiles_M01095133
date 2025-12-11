import streamlit as st
import sqlite3
import bcrypt
from data.db import connect_database, DATA_DIR
from data.users import get_user_by_username
from services.user_service import register_user

from pathlib import Path

def connect_database():
    return sqlite3.connect(DATA_DIR / "intelligence_platform.db")

# files inside the repository DATA folder
USERS_FILE = Path(DATA_DIR) / "users.txt"

def load_users():
    """Load users from DATA/users.txt into a dict {username: hashed_bytes}.
    Returns bytes for stored hashes (bcrypt expects bytes).
    """
    users = {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                username, hashed_pw = line.split(",", 1)
                users[username.strip()] = hashed_pw.strip().encode("utf-8")
    except FileNotFoundError:
        # No users file yet
        pass
    return users

def save_user(username, password):
    """Save new user to DATA/users.txt and to the SQLite users table.
    Returns True on success, False otherwise.
    """
    # hash password and write to file
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    try:
        USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(USERS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{username},{hashed}\n")
    except Exception:
        return False

    # also write to database (create table if needed via app.data.db)
    try:
        conn = connect_database()
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hashed, 'user')
        )
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Database error: {e}")
    return False

# ---------- Initialise session state ----------
if "users" not in st.session_state:
    # Very simple in-memory "database": {username: password}
    st.session_state.users = load_users()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

st.title("🔐 Welcome")

# If already logged in, go straight to dashboard (optional)
if st.session_state.logged_in:
    st.success(f"Already logged in as **{st.session_state.username}**.")
    if st.button("Go to dashboard"):
        # Use the official navigation API to switch pages
        st.switch_page("pages/1_IT.py")  # path is relative to Home.py :contentReference[oaicite:1]{index=1}
    st.stop()  # Don’t show login/register again

# ---------- Tabs: Login / Register ----------
tab_login, tab_register = st.tabs(["Login", "Register"])

# ----- LOGIN TAB -----
with tab_login:
    st.subheader("Login")

    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log in", type="primary"):
        user = get_user_by_username(login_username)
        if user:
            # DB row tuple is (id, username, password_hash, role) — use index 2
            stored_hash = user[2].encode("utf-8")
            password_bytes = login_password.encode("utf-8")

            if bcrypt.checkpw(password_bytes, stored_hash):
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.success(f"Welcome back, {login_username}!")
                st.switch_page("pages/1_IT.py")
            else:
                st.error("Invalid username or password.")
        else:
            st.error("Invalid username or password.")

# ----- REGISTER TAB -----
with tab_register:
    st.subheader("Register")

    new_username = st.text_input("Choose a username", key="register_username")
    new_password = st.text_input("Choose a password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm password", type="password", key="register_confirm")

    if st.button("Create account"):
        if not new_username or not new_password:
            st.warning("Please fill in all fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            success, message = register_user(new_username, new_password, role="user")
            if success:
                st.success(message)
                st.info("Tip: Go to the Login tab and sign in with your new account.")
            else:
                st.error(message)