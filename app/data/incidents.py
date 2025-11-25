import pandas as pd
from app.data.db import connect_database

def load_csv_to_table(conn, csv_path, table_name):
    """Load a CSV file into a database table using pandas."""
    if not csv_path.exists():
        print(f"File not found: {csv_path}. Skipping load.")
        return 0
    
    try:
        df = pd.read_csv(csv_path)
        # Use to_sql for efficient bulk loading
        df.to_sql(name=table_name, con=conn, if_exists='append', index=False)
        print(f"Loaded {len(df)} rows into '{table_name}' from {csv_path.name}")
        return len(df)
    except Exception as e:
        print(f"Error loading {csv_path.name} into {table_name}: {e}")
        return 0 

def insert_incident(date, incident_type, severity, status, description, reported_by=None):
    """Insert new incident."""
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cyber_incidents 
        (date, incident_type, severity, status, description, reported_by)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (date, incident_type, severity, status, description, reported_by))
    conn.commit()
    incident_id = cursor.lastrowid
    conn.close()
    return incident_id # Returns the new incident ID

def get_all_incidents():
    """Get all incidents as DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents ORDER BY id DESC",
        conn
    )
    conn.close()
    return df # Returns DataFrame of all incidents

def update_incident_status(conn, incident_id, new_status):
    """UPDATE: Modify the status of an incident."""
    cursor = conn.cursor()
    
    query = "UPDATE cyber_incidents SET status = ? WHERE id = ?"
    cursor.execute(query, (new_status, incident_id))
    
    conn.commit()
    return cursor.rowcount # Returns number of rows updated

def delete_incident(conn, incident_id):
    """DELETE: Remove an incident from the database."""
    cursor = conn.cursor()
    
    query = "DELETE FROM cyber_incidents WHERE id = ?"
    cursor.execute(query, (incident_id,))
    
    conn.commit()
    return cursor.rowcount # Returns number of rows deleted