import streamlit as st
import altair as alt
from openai import OpenAI
from data.db import connect_database
from data.tickets import(
   insert_ticket, get_all_tickets, update_ticket_status, delete_ticket
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
    st.error("You must be logged in to view the IT Tickets dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")   # back to the first page
    st.stop()

# If logged in, show dashboard content
st.title("📌 IT Dashboard")

conn = connect_database("DATA/intelligence_platform.db")
tickets = get_all_tickets(conn)

st.set_page_config(page_title="IT Dashboard", page_icon="📌", layout="wide")

# Tabs
tab_analytics, tab_tickets, tab_chatbot = st.tabs(["Analytics", "Ticket Manager", "IT Chatbot"])

with tab_analytics:
    st.header("Charts")

    # Visualization
    st.subheader("Tickets by Priority")
    priority_counts = tickets["priority"].value_counts().reset_index()
    priority_counts.columns = ["priority", "count"]
    
    custom_colors = alt.Scale(
        domain=["Critical", "High", "Medium", "Low"],
        range=["#D62728","#FF7F0E", "#FFC300", "#2CA02C"]
    )
    
    chart_priority = alt.Chart(priority_counts).mark_bar().encode(
        x=alt.X("priority", sort="-y", title="Ticket Priority"),
        y=alt.Y("count", title="Number of Tickets"),
        color=alt.Color("priority", scale=custom_colors, legend=alt.Legend(title="Priority"))
    )
    st.altair_chart(chart_priority)

    st.subheader("Tickets by Status")
    status_counts = tickets["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]

    custom_colors = alt.Scale(
        domain=["Open", "In Progress", "Closed", "Resolved"],
        range=["#595959","#A6A6A6", "#D9D9D9", "#2E2E2E"]
    )

    chart_status = (alt.Chart(status_counts).mark_bar().encode(
        y=alt.Y("status", sort="-y", title="Status"),
        x=alt.X("count", title="Count"),
        color=alt.Color(
            "status",
            sort=["Resolved", "Open", "In Progress", "Closed"],
            scale=alt.Scale(range=["#2E2E2E","#595959", "#A6A6A6", "#D9D9D9" ]),
            legend=alt.Legend(title="Status")
        )
    )
)
    st.altair_chart(chart_status)

    st.subheader("Tickets by Category")
    category_counts = tickets["category"].value_counts().reset_index()
    category_counts.columns = ["category", "count"]

    chart_category = alt.Chart(category_counts).mark_bar(color="#2C7FB8").encode(
        x=alt.X("category", sort="-y", title="Ticket Category"),
        y=alt.Y("count", title="Number of Tickets")
    )

    st.altair_chart(chart_category)

with tab_tickets:
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
    st.dataframe(tickets)

    st.subheader("⚙️ Manage Tickets")
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

with tab_chatbot:
    st.title("💬 ShaiahGPT - IT Chatbot")
    st.caption("Ask me anything about your IT issues. I'm here to help!")

    system_prompt = {
    "role": "system",
    "content": (
        "You are an experienced IT support technician. Respond to users with clear, professional advice. "
        "Use technical terminology when appropriate, and always aim to troubleshoot or guide the user toward a solution. "
        "Be concise, helpful, and confident."
    )
}

    if 'it_messages' not in st.session_state:
        st.session_state.it_messages = [system_prompt]

    #Sidebar with controls
    with st.sidebar:
        st.subheader("Chat Controls")

        message_count = len([m for m in st.session_state.it_messages if m["role"]!= "system"])
        st.metric("Messages", message_count)

        # Clear chat button
        if st.button("🗑️ Clear IT Chat", use_container_width=True):
            st.session_state.it_messages = []
            st.rerun()

        # Model
        model = "gpt-4.1-mini"

        # Temperature slider
        temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=1.0, step=0.1, help="Controls the randomness of the AI's responses.")

    # Display previous messages
    for message in st.session_state.it_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    prompt = st.chat_input("Type your message here...")

    if prompt:
        #Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        #Add user message to session state
        st.session_state.it_messages.append({
            "role": "user",
            "content": prompt
        })

        #Call OpenAI API with streaming
        with st.spinner("Thinking..."):
            completion = client.chat.completions.create(
                model=model,
                messages=st.session_state.it_messages,
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

        st.session_state.it_messages.append({
            "role": "assistant",
            "content": full_reply
        })
