import sqlite3
import pandas as pd

def insert_dataset(dataset_name, category, source, last_updated, record_count, file_size_mb):
    """CREATE: Insert a new dataset metadata record into the database."""
    conn = sqlite3.connect("data1/intelligence_platform.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO datasets_metadata 
        (dataset_name, category, source, last_updated, record_count, file_size_mb)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (dataset_name, category, source, last_updated, record_count, file_size_mb))

    conn.commit()
    conn.close()
    return cursor.lastrowid

def get_all_datasets():
    """READ: Retrieve all dataset metadata records as a pandas DataFrame."""
    conn = sqlite3.connect("data1/intelligence_platform.db")
    df = pd.read_sql_query("SELECT * FROM datasets_metadata ORDER BY last_updated DESC", conn)
    conn.close()
    return df

def update_dataset(dataset_id, dataset_name=None, category=None, source=None, last_updated=None, record_count=None, file_size_mb=None):
    """UPDATE: Modify dataset metadata details."""
    conn = sqlite3.connect("data1/intelligence_platform.db")
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if dataset_name:
        updates.append("dataset_name = ?")
        params.append(dataset_name)
    if category:
        updates.append("category = ?")
        params.append(category)
    if source:
        updates.append("source = ?")
        params.append(source)
    if last_updated:
        updates.append("last_updated = ?")
        params.append(last_updated)
    if record_count is not None:
        updates.append("record_count = ?")
        params.append(record_count)
    if file_size_mb is not None:
        updates.append("file_size_mb = ?")
        params.append(file_size_mb)
    if not updates:
        conn.close()
        return 0  # nothing to update
    
    # build final SQL query
    set_clause = ", ".join(updates)
    sql = f"UPDATE datasets_metadata SET {set_clause} WHERE id = ?"

    params.append(dataset_id)

    try:
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount
    except sqlite3.DatabaseError as e:
        print(f"Database error during update: {e}")
        return False
    
def delete_dataset(dataset_name):
    """DELETE: Remove a dataset metadata record from the database by dataset_name."""
    conn = sqlite3.connect("data1/intelligence_platform.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM datasets_metadata WHERE id = ?", (dataset_name,))
    conn.commit()
    rows_deleted = cursor.rowcount
    conn.close()
    return rows_deleted