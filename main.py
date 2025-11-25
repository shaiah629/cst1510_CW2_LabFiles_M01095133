from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.services.user_service import register_user, login_user, migrate_users_from_file
from app.data.incidents import insert_incident, get_all_incidents

def main():
    print("=" * 60)
    print("Week 8: Database Demo")
    print("=" * 60)
    
    # 1. Establish the connection for all operations that need it
    conn = connect_database() 
    
    try:
        # 1. Setup database: Creates the tables in the NEW .db file
        create_all_tables(conn)

        # 2. Migrate users (Function handles its own connection/commit)
        migrate_users_from_file()
        
        # 3. Test authentication (Functions handle their own connection/commit)
        # Note: The 'alice' user registered here will now use the correct schema
        success, msg = register_user("alice", "SecurePass123!", "analyst")
        print(f"Registration status: {msg}")
        
        success, msg = login_user("alice", "SecurePass123!")
        print(f"Login status: {msg}")
        
        # 4. Test CRUD 
        # 💡 FIX: Pass the 'conn' object as the first argument
        incident_id = insert_incident(
            conn, # <--- CONNECTION PASSED HERE
            "2024-11-05",
            "Phishing",
            "High",
            "Open",
            "Suspicious email detected",
            "alice"
        )
        print(f"Created incident #{incident_id}")

        # 5. Query data
        # 💡 FIX: Pass the 'conn' object as the argument
        df = get_all_incidents(conn) 
        print(f"Total incidents: {len(df)}")
        
    except Exception as e:
        print(f"\n--- FATAL ERROR --- \nAn error occurred: {e}")
        
    finally:
        # 6. Ensure connection is closed once all database work is finished
        if conn:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    main()