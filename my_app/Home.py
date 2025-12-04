import streamlit as st
import bcrypt
import os

#load users from users.txt file into session state
def load_users(filename="user.txt"):
    """Load users from file into a dictionary {username: hashed_password}"""
    users = {}
    if os.path.exists(filename):
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    username, hashed_pw = line.split(",", 1)
                    users[username] = hashed_pw.encode("utf-8")  # store as bytes
    return users

def save_user(username, password, filename="user.txt"):
    """Hash password and append new user to file"""
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    with open(filename, "a") as f:
        f.write(f"{username},{hashed_pw.decode('utf-8')}\n")

# ---------- Initialise session state ----------
if "users" not in st.session_state:
    # Very simple in-memory "database": {username: password}
    st.session_state.users = {}

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
        st.switch_page("pages/1_Dashboard.py")  # path is relative to Home.py :contentReference[oaicite:1]{index=1}
    st.stop()  # Don’t show login/register again

# ---------- Tabs: Login / Register ----------
tab_login, tab_register = st.tabs(["Login", "Register"])

# ----- LOGIN TAB -----
with tab_login:
    st.subheader("Login")

    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log in", type="primary"):
        # Simple credential check (for teaching only – not secure!)
        users = st.session_state.users
        if login_username in users:
            stored_hash = users[login_username]

            if bcrypt.checkpw(login_password.encode("utf-8"), stored_hash):
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.success(f"Welcome back, {login_username}! ")
                st.switch_page("pages/1_Dashboard.py")
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
        # Basic checks – again, just for teaching
        if not new_username or not new_password:
            st.warning("Please fill in all fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        elif new_username in st.session_state.users:
            st.error("Username already exists. Choose another one.")
        else:
            # "Save" user in our simple in-memory store
            hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
            st.session_state.users[new_username] = hashed_pw
            
            save_user(new_username, new_password)
            
            st.success("Account created! You can now log in from the Login tab.")
            st.info("Tip: go to the Login tab and sign in with your new account.")