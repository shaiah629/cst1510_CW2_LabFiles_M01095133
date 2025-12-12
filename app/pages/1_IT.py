import streamlit as st
from data.db import connect_database
from data.tickets import(
   insert_ticket, get_all_tickets, update_ticket_status, delete_ticket
)

conn = connect_database()

# Ensure state keys exist (in case user opens this page first)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the IT Tickets dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")   # back to the first page
    st.stop()

# If logged in, show dashboard content
st.title("🎟️ IT Tickets")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")

conn = connect_database("DATA/intelligence_platform.db")
tickets = get_all_tickets(conn)
st.dataframe(tickets)

# Dashboard metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Tickets", len(tickets))

with col2:
    priority = tickets[tickets["priority"].isin(["High", "Critical"])].shape[0]
    st.metric("High Priority Tickets", priority)

with col3:
    open_tickets = tickets[tickets["status"].isin(["Open", "In Progress"])].shape[0]
    st.metric("Open Tickets", open_tickets)

subject_counts = tickets["subject"].value_counts().to_dict()
st.bar_chart(subject_counts)

# Sidebar filters
st.subheader("Manage Tickets")
cola, colb, colc, = st.columns(3)
if "form" not in st.session_state:
    st.session_state.form = None

with cola:
    if st.button("Insert Ticket"):
        st.session_state.form = "insert"

with colb:
    if st.button("Update Ticket"):
        st.session_state.form = "update"

with colc:
    if st.button("Delete Ticket"):
        st.session_state.form = "delete"

#Insert / Update / Delete
if st.session_state.form == "insert":
    with st.form("new_ticket"):
        subject = st.text_input("Subject")
        category = st.text_input("Category")
        description = st.text_area("Description")
        priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
        created_date = st.date_input("Created Date")
        resolved_date = st.date_input("Resolved Date", value=None)
        assigned_to = st.text_input("Assigned To")
        submitted = st.form_submit_button("Insert Ticket")

        if submitted:
            ticket_id = insert_ticket(conn, priority, status, category, subject, description, created_date, resolved_date, assigned_to or None)
            st.success(f"Ticket #{ticket_id} inserted successfully.")
            st.rerun()

if st.session_state.form == "update":
    with st.form("update_ticket"):
        ticket_id = st.text_input("Ticket ID to Update")
        new_status = st.selectbox("New Status", ["Open", "In Progress", "Resolved", "Closed"])
        resolved_date = st.date_input("Resolved Date", value=None)
        submitted = st.form_submit_button("Update Ticket")

        if submitted:
            ticket_id = update_ticket_status(conn, ticket_id, new_status, resolved_date or None)
            st.success(f"Ticket #{ticket_id} updated successfully.")
            st.rerun()

if st.session_state.form == "delete":
    with st.form("delete_ticket"):
        ticket_id = st.text_input("Ticket ID to Delete (e.g., TICKET-001)")
        submitted = st.form_submit_button("Delete Ticket")

        if submitted:
            rows_deleted = delete_ticket(conn, ticket_id)
            if rows_deleted:
                st.success(f"Ticket #{ticket_id} deleted successfully.")
            else:
                st.error(f"Ticket #{ticket_id} not found.")
            st.rerun()

# Logout button
st.divider()
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.info("You have been logged out.")
    st.switch_page("Home.py")