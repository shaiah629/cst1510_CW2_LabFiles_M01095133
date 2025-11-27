import pandas as pd
from app.data.db import connect_database
from pathlib import Path

def load_csv_to_table(conn, csv_path: Path, table_name: str):
    """Load a CSV file into a database table using pandas."""
    if not csv_path.exists():
        print(f"  - ⚠️ File not found: {csv_path.name}. Skipping load.")
        return 0
    
    try:
        df = pd.read_csv(csv_path)
        #use to_sql for efficient bulk loading
        #if_exists='append' adds to existing data
        df.to_sql(name=table_name, con=conn, if_exists='append', index=False)
        print(f"  - ✅ Loaded {len(df)} rows into '{table_name}' from {csv_path.name}")
        return len(df)
    except Exception as e:
        print(f"  - ❌ Error loading {csv_path.name} into {table_name}: {e}")
        return 0

def insert_incident(conn, date, incident_type, severity, status, description, reported_by=None):
    """CREATE: Insert a new cyber incident into the database."""
    cursor = conn.cursor()
    
    query = """
    INSERT INTO cyber_incidents 
    (date, incident_type, severity, status, description, reported_by)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    #secure parameterized query
    cursor.execute(
        query, 
        (date, incident_type, severity, status, description, reported_by)
    )
    conn.commit()
    return cursor.lastrowid

def get_all_incidents(conn):
    """READ: Retrieve all incidents as a DataFrame."""
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents ORDER BY id DESC",
        conn
    )
    return df

def update_incident_status(conn, incident_id, new_status):
    """UPDATE: Modify the status of an incident."""
    cursor = conn.cursor()
    
    query = "UPDATE cyber_incidents SET status = ? WHERE id = ?"
    cursor.execute(query, (new_status, incident_id))
    
    conn.commit()
    return cursor.rowcount

def delete_incident(conn, incident_id):
    """DELETE: Remove an incident from the database."""
    cursor = conn.cursor()
    
    query = "DELETE FROM cyber_incidents WHERE id = ?"
    cursor.execute(query, (incident_id,))
    
    conn.commit()
    return cursor.rowcount

def get_incidents_by_type_count(conn):
    """Analytical Query: Count incidents by type using SQL aggregation."""
    query = """
    SELECT incident_type, COUNT(*) as count
    FROM cyber_incidents
    GROUP BY incident_type
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df