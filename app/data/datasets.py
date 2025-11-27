import sqlite3

#connect to database
conn = sqlite3.connect('intelligence_platform.db')
cursor = conn.cursor()

#create datasets table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS datasets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        created_at TEXT NOT NULL
    );
""")

conn.commit()