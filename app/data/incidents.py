import pandas as pd
from app.data.db import connect_database

def insert_incident(conn, date, incident_type, severity, status, description, reported_by=None):
    """CREATE: Insert a new cyber incident into the database."""
    conn = connect_database()
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO cyber_incidents 
    (date, incident_type, severity, status, description, reported_by)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (date, incident_type, severity, status, description, reported_by))

    conn.commit()
    conn.close()
    return cursor.lastrowid

def get_all_incidents(conn):
    """READ: Retrieve all incidents as a DataFrame."""
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM cyber_incidents ORDER BY id DESC",
        conn
    )
    conn.close()
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