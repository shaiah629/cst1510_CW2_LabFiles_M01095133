import streamlit as st
import altair as alt
from openai import OpenAI
from data.db import connect_database
from data.incidents import (
    insert_incident, get_all_incidents, update_incident_status, delete_incident
)

conn = connect_database()

# Initialize OpenAI client with API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Ensure state keys exist (in case user opens this page first)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view Cyber Incidents.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")   # back to the first page
    st.stop()

# If logged in, show dashboard content
st.title("🚨 Cyber Incidents")

st.set_page_config(page_title="Cyber Incidents", page_icon="🚨", layout="wide")

conn = connect_database("DATA/intelligence_platform.db")
incidents = get_all_incidents(conn)

# Tab
tab_analytics, tab_incidents, tab_chatbot = st.tabs(["Analytics", "Incident Manager", "Cyber Chatbot"])
with tab_analytics:
    st.header("Charts")

    # Visualization
    st.subheader("Incidents by Severity")
    severity_counts = incidents["severity"].value_counts().reset_index()
    severity_counts.columns = ["severity", "count"]

    custom_colors = alt.Scale(
        domain=["Critical", "High", "Medium", "Low"],
        range=["#D62728","#FF7F0E", "#FFC300", "#2CA02C"]
    )

    chart_severity = alt.Chart(severity_counts).mark_bar().encode(
        x=alt.X("severity", sort="-y", title="Severity"),
        y=alt.Y("count", title="Number of incidents"),
        color=alt.Color("severity", scale=custom_colors, legend=alt.Legend(title="Severity"))
    )
    st.altair_chart(chart_severity)

    st.subheader("Incidents by Status")
    status_counts = incidents["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]

    custom_colors = alt.Scale(
        domain=["Open", "Closed", "Resolved"],
        range=["#595959","#A6A6A6","#2E2E2E"]
    )
    chart_status = (alt.Chart(status_counts).mark_bar().encode(
        y=alt.Y("status", sort="-y", title="Status"),
        x=alt.X("count", title="Count"),
        color=alt.Color(
            "status",
            sort=["Resolved", "Open", "Closed"],
            scale=alt.Scale(range=["#2E2E2E","#595959", "#A6A6A6"]),
            legend=alt.Legend(title="Status")
        )
    )
)
    st.altair_chart(chart_status)

    st.subheader("Incidents by Type")
    type_counts = incidents["incident_type"].value_counts().reset_index()
    type_counts.columns = ["incident_type", "count"]

    chart_type = alt.Chart(type_counts).mark_bar(color="#2C7FB8").encode(
        x=alt.X("incident_type", sort="-y", title="Incident Type"),
        y=alt.Y("count", title="Number of Incidents")
    )
    st.altair_chart(chart_type)

with tab_incidents:
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
    st.dataframe(incidents)

    st.subheader("⚙️ Manage Incidents")
    cola, colb, colc, = st.columns(3)

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

with tab_chatbot:
    st.title("💬 ShaiahGPT - Cyber Chatbot")
    st.caption("Ask me anything about your cyber issues. I'm here to help!")

    system_prompt = {
    "role": "system",
    "content": (
        "You are a seasoned cybersecurity expert. Respond to users with clear, authoritative guidance on "
        "cyber threats, security best practices, and risk mitigation strategies. Use precise technical terminology "
        "when appropriate, and always aim to strengthen the user's security posture or guide them toward a safe solution. "
        "Be concise, professional, and confident, while ensuring your advice reflects modern cybersecurity standards."
    )
}

    if 'cyber_messages' not in st.session_state:
        st.session_state.cyber_messages = [system_prompt]

    #Sidebar with controls
    with st.sidebar:
        st.subheader("Chat Controls")

        message_count = len([m for m in st.session_state.cyber_messages if m["role"]!= "system"])
        st.metric("Messages", message_count)

        # Clear chat button
        if st.button("🗑️ Clear Cyber Chat", use_container_width=True):
            st.session_state.cyber_messages = []
            st.rerun()

        # Model
        model = "gpt-4.1-mini"

        # Temperature slider
        temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=1.0, step=0.1, help="Controls the randomness of the AI's responses.")

    # Display previous messages
    for message in st.session_state.cyber_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    prompt = st.chat_input("Type your message here...")

    if prompt:
        #Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        #Add user message to session state
        st.session_state.cyber_messages.append({
            "role": "user",
            "content": prompt
        })

        #Call OpenAI API with streaming
        with st.spinner("Thinking..."):
            completion = client.chat.completions.create(
                model=model,
                messages=st.session_state.cyber_messages,
                temperature=temperature,
                stream=True
            )

        with st.chat_message("assistant"):
            container = st.empty()
            full_reply = ""

            for chunk in completion:
                delta = chunk.choices[0].delta
                if delta.content:
                    full_reply += delta.content
                    container.markdown(full_reply + " ") #Add cursor effect

            container.markdown(full_reply)

        st.session_state.cyber_messages.append({
            "role": "assistant",
            "content": full_reply
        })