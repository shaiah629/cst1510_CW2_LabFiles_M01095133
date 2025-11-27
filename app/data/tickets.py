import pandas as pd
import sqlite3

def insert_ticket(conn: sqlite3.Connection, ticket_id: str, priority: str, status: str, 
                  category: str, subject: str, description: str, 
                  created_date: str, resolved_date: str = None, assigned_to: str = None):
    """
    CREATE: Insert a new IT ticket record into the database.
    Returns: The ID of the newly created record.
    """
    cursor = conn.cursor()
    
    query = """
    INSERT INTO it_tickets 
    (ticket_id, priority, status, category, subject, description, 
     created_date, resolved_date, assigned_to)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    #secure parameterized query
    cursor.execute(
        query, 
        (ticket_id, priority, status, category, subject, description, 
         created_date, resolved_date, assigned_to)
    )
    conn.commit()
    return cursor.lastrowid

def get_all_tickets(conn: sqlite3.Connection):
    """
    READ: Retrieve all IT ticket records as a pandas DataFrame.
    """
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets ORDER BY created_date DESC",
        conn
    )
    return df

def get_tickets_by_status_count(conn: sqlite3.Connection):
    """
    ANALYTICAL QUERY: Count the number of tickets grouped by their status.
    """
    query = """
    SELECT status, COUNT(*) as count
    FROM it_tickets
    GROUP BY status
    ORDER BY count DESC
    """
    df = pd.read_sql_query(query, conn)
    return df

def update_ticket_status(conn: sqlite3.Connection, ticket_id: str, new_status: str, resolved_date: str = None):
    """
    UPDATE: Modify the status and optionally the resolution date for a ticket.
    
    Returns: The number of rows updated (should be 1).
    """
    cursor = conn.cursor()
    
    if new_status.lower() == 'closed' and not resolved_date:
        #if closing, set resolved_date to today if not provided
        resolved_date = pd.to_datetime('today').strftime('%Y-%m-%d')
        
    query = "UPDATE it_tickets SET status = ?, resolved_date = ? WHERE ticket_id = ?"
    cursor.execute(query, (new_status, resolved_date, ticket_id))
    
    conn.commit()
    return cursor.rowcount

def delete_ticket(conn: sqlite3.Connection, ticket_id: str):
    """
    DELETE: Remove an IT ticket record from the database by ticket_id.
    
    Returns: The number of rows deleted (should be 1 or 0).
    """
    cursor = conn.cursor()
    
    query = "DELETE FROM it_tickets WHERE ticket_id = ?"
    cursor.execute(query, (ticket_id,))
    
    conn.commit()
    return cursor.rowcount