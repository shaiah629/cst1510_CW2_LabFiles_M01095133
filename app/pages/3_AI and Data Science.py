import streamlit as st
import altair as alt
import pandas as pd
from openai import OpenAI
from data.datasets import (
    insert_dataset, get_all_datasets, update_dataset, delete_dataset
)

DB_PATH = "DATA/intelligence_platform.db"

# Initialize OpenAI client with API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Ensure state keys exist (in case user opens this page first)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the Datasets Metadata dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")   # back to the first page
    st.stop()

# If logged in, show dashboard content
st.title("📁 AI and Data Science")

st.set_page_config(page_title="AI and Data Science", page_icon="📁", layout="wide")

datasets = get_all_datasets()

#Tabs
tab_analytics, tab_data, tab_chatbot = st.tabs(["Analytics", "Dataset Manager", "AI and Data Science Chatbot"])
with tab_analytics:
    st.header("Charts")

    st.subheader("Dataset by Record")
    record_counts = datasets["record_count"].value_counts().reset_index()
    record_counts.columns = ["record_count", "count"]

    chart_records = alt.Chart(record_counts).mark_bar().encode(
        x=alt.X("record_count", sort="-y", title="Record Count"),
        y=alt.Y("count", title="Number of Datasets"),
        color=alt.Color("record_count", legend=None)
    )
    st.altair_chart(chart_records)

    st.subheader("Dataset by Size")

    size_counts = datasets["file_size_mb"].value_counts().reset_index()
    size_counts.columns = ["file_size_mb", "count"]

    chart_size = alt.Chart(size_counts).mark_bar().encode(
        x=alt.X("file_size_mb:Q", sort="-y", title="File Size (MB)"),
        y=alt.Y("count:Q",title="Number of Datasets"),
        color=alt.Color("file_size_mb:Q",legend=None)
    )
    st.altair_chart(chart_size, use_container_width=True)

with tab_data:
    # Dashboard metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Datasets", len(datasets))

    with col2:
        total_records = datasets["record_count"].sum()
        st.metric("Total Records", total_records)

    with col3:
        total_size = datasets["file_size_mb"].sum()
        st.metric("Total Size (MB)", f"{total_size:.2f}")

    st.dataframe(datasets)

    st.subheader("⚙️ Manage Datasets")
    cola, colb, colc = st.columns(3)

    with cola:
        if st.button("Insert Metadata"):
            st.session_state.form = "insert"

    with colb:
        if st.button("Update Metadata"):
            st.session_state.form = "update"

    with colc:
        if st.button("Delete Metadata"):
            st.session_state.form = "delete"

    #Insert / Update / Delete
    if st.session_state.form == "insert":
        with st.form("new_dataset"):
            dataset_name = st.text_input("Dataset Name")
            category = st.text_input("Category")
            source = st.text_input("Source")
            last_updated = st.date_input("Last Updated")
            record_count = st.number_input("Record Count", min_value=0, step=1)
            file_size_mb = st.number_input("File Size (MB)", min_value=0.0, step=0.01)
            submitted = st.form_submit_button("Insert Metadata")

            if submitted:
                dataset_id = insert_dataset(dataset_name, category, source, last_updated, record_count, file_size_mb)
                st.success(f"Dataset metadata #{dataset_id} inserted successfully.")
                st.rerun()

    if st.session_state.form == "update":
        with st.form("update_dataset"):
            dataset_id = st.number_input("Dataset ID to Update", min_value=1, step=1)
            dataset_name = st.text_input("Dataset Name (leave blank to keep unchanged)")
            category = st.text_input("Category (leave blank to keep unchanged)")
            source = st.text_input("Source (leave blank to keep unchanged)")
            last_updated = st.date_input("Last Updated (leave blank to keep unchanged)", value=None)
            record_count = st.number_input("Record Count (leave as 0 to keep unchanged)", min_value=0, step=1)
            file_size_mb = st.number_input("File Size (MB) (leave as 0.0 to keep unchanged)", min_value=0.0, step=0.01)
            submitted = st.form_submit_button("Update Metadata")

            if submitted:
                updated_rows = update_dataset(dataset_id, dataset_name or None, category or None, source or None, last_updated or None, record_count or None, file_size_mb or None)
                if updated_rows:
                    st.success(f"Dataset metadata #{dataset_id} updated successfully.")
                else:
                    st.info("No changes made.")
                st.rerun()

    if st.session_state.form == "delete":
        with st.form("delete_dataset"):
            dataset_id = st.number_input("Dataset ID to delete")
            submitted = st.form_submit_button("Delete Metadata")

            if submitted:
                rows_deleted = delete_dataset(dataset_id)
                if rows_deleted:
                    st.success(f"Dataset metadata #{dataset_id} deleted successfully.")
                else:
                    st.error(f"No dataset metadata found with ID #{dataset_id}.")
                st.rerun()

with tab_chatbot:
    st.title("💬 ShaiahGPT - AI and Data Science Chatbot")
    st.caption("Ask me anything about your AI and Data Science issues. I'm here to help!")

    system_prompt = {
    "role": "system",
    "content": (
        "You are a seasoned AI and Data Science expert. Respond to users with clear, authoritative guidance on "
        "machine learning, artificial intelligence, data analysis, and statistical modeling. Use precise technical terminology "
        "when appropriate, and always aim to help the user understand concepts, improve their models, or interpret results effectively. "
        "Be concise, professional, and confident, while ensuring your advice reflects modern best practices in AI and data science."
    )
}

    if 'ai_messages' not in st.session_state:
        st.session_state.ai_messages = [system_prompt]

    #Sidebar with controls
    with st.sidebar:
        st.subheader("Chat Controls")

        message_count = len([m for m in st.session_state.ai_messages if m["role"]!= "system"])
        st.metric("Messages", message_count)

        # Clear chat button
        if st.button("🗑️ Clear AI and Data Science Chat", use_container_width=True):
            st.session_state.ai_messages = []
            st.rerun()

        # Model
        model = "gpt-4.1-mini"

        # Temperature slider
        temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=1.0, step=0.1, help="Controls the randomness of the AI's responses.")

    # Display previous messages
    for message in st.session_state.ai_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    prompt = st.chat_input("Type your message here...")

    if prompt:
        #Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        #Add user message to session state
        st.session_state.ai_messages.append({
            "role": "user",
            "content": prompt
        })

        #Call OpenAI API with streaming
        with st.spinner("Thinking..."):
            completion = client.chat.completions.create(
                model=model,
                messages=st.session_state.ai_messages,
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

        st.session_state.ai_messages.append({
            "role": "assistant",
            "content": full_reply
        })