import sqlite3
import pandas as pd
from typing import Any, Iterable


class DatabaseManager:
    """Handles SQLite database connections and queries safely."""

    def __init__(self, db_path: str):
        self._db_path = db_path
        self._connection: sqlite3.Connection | None = None

    def connect(self) -> None:
        """Connect to the SQLite database if not already connected."""
        if self._connection is None:
            self._connection = sqlite3.connect(self._db_path)

    def close(self) -> None:
        """Close the SQLite connection if open."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def execute_query(self, sql: str, params: Iterable[Any] = ()) -> sqlite3.Cursor:
        """
        Execute a write query (INSERT, UPDATE, DELETE).
        Returns the cursor for additional info if needed.
        """
        self.connect()
        with self._connection:
            cur = self._connection.cursor()
            cur.execute(sql, tuple(params))
        return cur

    def fetch_one(self, sql: str, params: Iterable[Any] = ()):
        """Fetch a single row from a query."""
        self.connect()
        cur = self._connection.cursor()
        cur.execute(sql, tuple(params))
        return cur.fetchone()

    def fetch_all(self, sql: str, params: Iterable[Any] = ()):
        """Fetch all rows from a query."""
        self.connect()
        cur = self._connection.cursor()
        cur.execute(sql, tuple(params))
        return cur.fetchall()

    def fetch_dataframe(self, query: str, params: tuple = ()) -> pd.DataFrame:
        """
        Execute a SQL query and return the result as a pandas DataFrame.
        """
        self.connect()
        cur = self._connection.cursor()
        cur.execute(query, params)
        columns = [desc[0] for desc in cur.description]
        data = cur.fetchall()
        return pd.DataFrame(data, columns=columns)
