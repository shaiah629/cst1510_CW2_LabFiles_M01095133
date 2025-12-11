import streamlit as st
import sqlite3
import pandas as pd
from data.datasets import (
    insert_dataset, get_all_datasets, update_dataset, delete_dataset
)

DB_PATH = "data1/intelligence_platform.db"

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
st.title("🗃️ Datasets Metadata")
st.success(f"Hello, **{st.session_state.username}**! You are logged in.")

datasets = get_all_datasets()
st.dataframe(datasets)

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

category_counts = datasets["category"].value_counts().to_dict()
st.bar_chart(category_counts)

# Sidebar filters
st.subheader("Manage Datasets Metadata")
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