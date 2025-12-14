import pandas as pd
from services.database_manager import DatabaseManager

class TicketManager:
    """Manages IT ticket operations using a DatabaseManager."""

    def __init__(self, db: DatabaseManager):
        self._db = db

    def insert_ticket(self, priority: str, status: str, category: str, subject: str,
                      description: str, created_date: str, resolved_date: str, assigned_to: str) -> int:
        cursor = self._db.execute_query("SELECT COUNT(*) FROM it_tickets")
        count = cursor.fetchone()[0] + 1
        ticket_id = f"TICKET-{count:03d}"

        query = """
        INSERT INTO it_tickets 
        (ticket_id, priority, status, category, subject, description, 
         created_date, resolved_date, assigned_to)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self._db.execute_query(query, (
            ticket_id, priority, status, category, subject,
            description, created_date, resolved_date, assigned_to
        ))
        return ticket_id

    def get_all_tickets(self) -> pd.DataFrame:
        return pd.read_sql_query(
            "SELECT * FROM it_tickets ORDER BY created_date DESC",
            self._db._connection
        )

    def get_tickets_by_status_count(self) -> pd.DataFrame:
        query = """
        SELECT status, COUNT(*) as count
        FROM it_tickets
        GROUP BY status
        ORDER BY count DESC
        """
        return pd.read_sql_query(query, self._db._connection)

    def update_ticket_status(self, ticket_id: str, new_status: str, resolved_date: str = None) -> int:
        if new_status.lower() == 'closed' and not resolved_date:
            resolved_date = pd.to_datetime('today').strftime('%Y-%m-%d')

        query = "UPDATE it_tickets SET status = ?, resolved_date = ? WHERE ticket_id = ?"
        cursor = self._db.execute_query(query, (new_status, resolved_date, ticket_id))
        return cursor.rowcount

    def delete_ticket(self, ticket_id: str) -> int:
        query = "DELETE FROM it_tickets WHERE ticket_id = ?"
        cursor = self._db.execute_query(query, (ticket_id,))
        return cursor.rowcount