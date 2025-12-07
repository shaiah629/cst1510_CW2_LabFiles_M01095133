import pandas as pd
import sqlite3
from app.data.db import connect_database, DATA_DIR
from app.data.schema import create_all_tables, migrate_users_from_file
from app.services.user_service import register_user, login_user
from app.data.incidents import (
    load_csv_to_table, insert_incident, get_all_incidents, 
    update_incident_status, delete_incident, get_incidents_by_type_count
)
DB_PATH = DATA_DIR / "intelligence_platform.db"

def load_all_csv_data(conn):
    """Load all domain CSV files into their respective tables."""
    total_rows = 0
    print("\nAttempting to load data from CSV files...")
    
    #load cyber incidents
    total_rows += load_csv_to_table(
        conn, DATA_DIR / "cyber_incidents.csv", "cyber_incidents"
    )
    #load datasets metadata
    total_rows += load_csv_to_table(
        conn, DATA_DIR / "datasets_metadata.csv", "datasets_metadata"
    )
    #laod it tickets
    total_rows += load_csv_to_table(
        conn, DATA_DIR / "it_tickets.csv", "it_tickets"
    )
    
    print(f"   Total rows successfully loaded across domains: {total_rows}")
    return total_rows

def main():
    print("=" * 60)
    print("Week 8: Database Demo and Setup")
    print("=" * 60)
    
    #1. connect to database
    conn = connect_database() 
    
    try:
        #2. create all tables
        print("[1/5] Creating all tables...")
        create_all_tables(conn)

        #3. migrate users from users.txt
        print("\n[2/5] Migrating users...")
        migrate_users_from_file()
        
        #4. load CSV data into tables
        print("\n[3/5] Loading CSV data...")
        load_all_csv_data(conn)
        
        #5. test authentication and CRUD operations
        print("\n[4/5] Testing Authentication and CRUD:")
        success, msg = register_user("alice", "SecurePass123!", "analyst")
        print(f"  Register: {'✅' if success else '❌'} {msg}")
        
        success, msg = login_user("alice", "SecurePass123!")
        print(f"  Login:    {'✅' if success else '❌'} {msg}")
        
        #6. test CRUD operations
        #CREATE
        incident_id = insert_incident(
            conn, #pass connection
            "2025-11-25", "Phishing", "High", "Open", 
            "Suspicious email targeted CEO", "alice"
        )
        print(f"  CREATE: ✅ Incident #{incident_id} created.")
        
        #UPDATE
        update_incident_status(conn, incident_id, "Resolved")
        df_status = pd.read_sql_query(f"SELECT status FROM cyber_incidents WHERE id = {incident_id}", conn)
        print(f"  UPDATE: ✅ Status updated to '{df_status['status'].iloc[0]}'.")
        
        #READ & ANALYTICS
        df_all = get_all_incidents(conn)
        print(f"  READ:   Total incidents found: {len(df_all)}")

        df_analysis = get_incidents_by_type_count(conn)
        print("\n  [5/5] Analytical Query (Incidents by Type):")
        print(df_analysis.head().to_string(index=False))

        #DELETE
        delete_incident(conn, incident_id)
        print(f"\n  DELETE: ✅ Test incident #{incident_id} deleted.")
        
    except sqlite3.OperationalError as e:
        print(f"\n--- DATABASE ERROR --- \nError: {e}")
        print("ACTION REQUIRED: You likely need to delete the old 'intelligence_platform.db' file from your DATA folder.")
        
    except Exception as e:
        print(f"\n--- FATAL ERROR --- \nAn error occurred: {e}")
        
    finally:
        #ensure connection is closed
        if conn:
            conn.close()
            print("\nDatabase connection closed.")
        print("\n" + "="*60)

if __name__ == "__main__":
    main()