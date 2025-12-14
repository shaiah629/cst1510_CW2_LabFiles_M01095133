import streamlit as st
import bcrypt
from services.database_manager import DatabaseManager
from services.auth_manager import AuthManager

db = DatabaseManager("database/platform.db")
auth = AuthManager(db)

# ---------- Initialise session state ----------
if "users" not in st.session_state:
    # Very simple in-memory "database": {username: password}
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

st.title("🔐 Welcome")

# ----- SIDEBAR -----
if st.sidebar.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.info("You have been logged out.")
    st.switch_page("1_Home.py")

# If already logged in, go straight to dashboard (optional)
if st.session_state.logged_in:
    st.success(f"Already logged in as **{st.session_state.username}**.")
    if st.button("Go to dashboard"):
        # Use the official navigation API to switch pages
        st.switch_page("pages/2_IT Operations.py")
    st.stop()  # Don’t show login/register again

# ---------- Tabs: Login / Register ----------
tab_login, tab_register = st.tabs(["Login", "Register"])

# ----- LOGIN TAB -----
with tab_login:
    st.subheader("Login")

    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log in", type="primary"):
        user = auth.login_user(login_username, login_password)
        if user:
            # DB row tuple is (id, username, password_hash, role) — use index 2
            stored_hash = user[2].encode("utf-8")
            password_bytes = login_password.encode("utf-8")

            if bcrypt.checkpw(password_bytes, stored_hash):
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.success(f"Welcome back, {login_username}!")
                st.switch_page("pages/2_IT Operations.py")
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
            success, message = auth.register_user(new_username, new_password, role="user")
            if success:
                st.success(message)
                st.info("Tip: Go to the Login tab and sign in with your new account.")
            else:
                st.error(message)