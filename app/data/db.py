import sqlite3
from pathlib import Path

#define paths for the DATA folder and the database file
DATA_DIR = Path("DATA")
DB_PATH = DATA_DIR / "intelligence_platform.db"

#ensure the DATA folder exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

def connect_database(db_path=DB_PATH):
    """
    Connect to the SQLite database.
    Creates the database file if it doesn't exist.
    """
    #the str() conversion ensures cross-platform path compatibility
    return sqlite3.connect(str(db_path))