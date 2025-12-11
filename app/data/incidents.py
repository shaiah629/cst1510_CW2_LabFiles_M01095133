import pandas as pd
from pathlib import Path
from data.db import connect_database

def load_csv_to_table(conn, csv_path, table_name: str):
    """Load a CSV file into a database table using pandas."""
    if not csv_path.exists():
        print(f"  - ⚠️ File not found: {csv_path.name}. Skipping load.")
    
    df = pd.read_csv(csv_path)
    df.to_sql(name=table_name, con=conn, if_exists='append', index=False)
    row_count = len(df)
    print(f"  - ✅ Loaded {len(df)} rows into '{table_name}' from {csv_path.name}")
    
    return row_count 
    
def load_all_csv_data(conn, directory, if_exists='append'):
    results = {}
    directory = Path(directory)

    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    for csv_file in directory.glob("*.csv"):
        table_name = csv_file.stem
        df = pd.read_csv(csv_file)

        df.to_sql(
            name=table_name,
            con=conn,
            if_exists=if_exists,
            index=False
        )

        row_count = len(df)
        results[table_name] = row_count
        print(f"✅ Loaded {row_count} rows into '{table_name}' from {csv_file.name}")

    return results

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