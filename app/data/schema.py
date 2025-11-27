#import connection utility
from app.data.db import connect_database

def create_users_table(conn):
    """Create the users table with security columns."""
    cursor = conn.cursor()
    # Ensure this SQL string is exactly correct
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,  <-- CHECK FOR THIS COMMA!
        password_hash TEXT NOT NULL,    <-- CHECK THIS SPELLING!
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(create_table_sql)
    conn.commit()
    print("  - ✅ Users table created.")

def create_cyber_incidents_table(conn):
    """Create the cyber_incidents table."""
    cursor = conn.cursor()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS cyber_incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        incident_type TEXT,
        severity TEXT,
        status TEXT,
        description TEXT,
        reported_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (reported_by) REFERENCES users(username) ON DELETE SET NULL
    )
    """
    cursor.execute(create_table_sql)
    conn.commit()
    print("  - ✅ Cyber Incidents table created.")

def create_datasets_metadata_table(conn):
    """Create the datasets_metadata table."""
    cursor = conn.cursor()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS datasets_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_name TEXT NOT NULL,
        category TEXT,
        source TEXT,
        last_updated TEXT,
        record_count INTEGER,
        file_size_mb REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(create_table_sql)
    conn.commit()
    print("  - ✅ Datasets Metadata table created.")

def create_it_tickets_table(conn):
    """Create the it_tickets table."""
    cursor = conn.cursor()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS it_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id TEXT UNIQUE NOT NULL,
        priority TEXT,
        status TEXT,
        category TEXT,
        subject TEXT NOT NULL,
        description TEXT,
        created_date TEXT,
        resolved_date TEXT,
        assigned_to TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(create_table_sql)
    conn.commit()
    print("  - ✅ IT Tickets table created.")

def create_all_tables(conn):
    """Create all tables in the database."""
    print("Creating all database tables...")
    create_users_table(conn)
    create_cyber_incidents_table(conn)
    create_datasets_metadata_table(conn)
    create_it_tickets_table(conn)
    print("All tables schema established.")