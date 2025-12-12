import sqlite3
from pathlib import Path

# Define paths
DATA_DIR = Path("DATA")
DB_PATH = DATA_DIR / "intelligence_platform.db"

def connect_database(db_path=DB_PATH):
    return sqlite3.connect(db_path)

print(" Imports successful!")
print(f" DATA folder: {DATA_DIR.resolve()}")
print(f" Database will be created at: {DB_PATH.resolve()}")