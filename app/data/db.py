#connects and closes the database
import sqlite3
from pathlib import Path

DATA_DIR = Path("Data")
DB_PATH = Path("DATA") / "intelligence_platform.db"

def connect_database(db_path=DB_PATH):
    """Connect to the SQLite database."""
    return sqlite3.connect(str(db_path))