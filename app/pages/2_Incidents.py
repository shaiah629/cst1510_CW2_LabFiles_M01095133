import streamlit as st
from data.db import connect_database
from data.incidents import (
    insert_incident, get_all_incidents, update_incident_status, delete_incident
)

conn = connect_database()

# Ensure state keys exist (in case user opens this page first)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the Cyber Incidents dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")   # back to the first page
    st.stop()

# If logged in, show dashboard content
st.title("🚨 Cyber Incidents")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")

conn = connect_database("data1/intelligence_platform.db")
incidents = get_all_incidents(conn)
st.dataframe(incidents)

# Dashboard metrics
col1, col2, col3 = st.columns(3)
with col1:
    st. metric("Total Incidents", len(incidents))

with col2:
    severity = incidents[incidents["severity"].isin(["High", "Critical"])].shape[0]
    st.metric("High Severity Incidents", severity)

with col3:
    open_incidents = incidents[incidents["status"].isin(["Open", "In Progress"])].shape[0]
    st.metric("Open Incidents", open_incidents)

category_counts = incidents["incident_type"].value_counts().to_dict()
st.bar_chart(category_counts)

# Sidebar filters
st.subheader("Manage Incidents")
cola, colb, colc = st.columns(3)

with cola:
    if st.button("Insert Incident"):
        st.session_state.form = "insert"

with colb:
    if st.button("Update Incident"):
        st.session_state.form = "update"

with colc:
    if st.button("Delete Incident"):
        st.session_state.form = "delete"

#Insert / Update / Delete
if st.session_state.form == "insert":
    with st.form("new_incident"):
        category = st.text_input("Incident Type")
        description = st.text_area("Description")
        severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
        status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
        date = st.date_input("Created Date")
        reported_by = st.text_input("Reported by")
        submitted = st.form_submit_button("Insert Incident")

    if submitted:
        incident_id = insert_incident(conn, date, category, severity, status, description, reported_by=None)
        st.success(f"Incident #{incident_id} inserted successfully.")
        st.rerun()

if st.session_state.form == "update":
    with st.form("update_incident"):
        incident_id = st.text_input("Incident ID")
        new_status = st.selectbox("New Status", ["Open", "In Progress", "Resolved", "Closed"])
        submitted = st.form_submit_button("Update Incident")

    if submitted:
        update_incident_status(conn, incident_id, new_status)
        st.success(f"Incident #{incident_id} updated successfully.")
        st.rerun()

if st.session_state.form == "delete":
    with st.form("delete_incident"):
        incident_id = st.text_input("Incident ID to Delete")
        submitted = st.form_submit_button("Delete Incident")

        if submitted:
            rows_deleted = delete_incident(conn, incident_id)
            if rows_deleted:
                st.success(f"Incident #{incident_id} deleted successfully.")
            else:
                st.error(f"Incident #{incident_id} not found.")