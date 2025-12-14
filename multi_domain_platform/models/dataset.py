import pandas as pd
from services.database_manager import DatabaseManager

class Dataset:
    """Represents a dataset and provides DB access to datasets_metadata table."""

    def __init__(self, db: DatabaseManager, dataset_id: int = None, dataset_name: str = None,
                 category: str = None, source: str = None, last_updated: str = None,
                 record_count: int = None, file_size_mb: float = None, created_at: str = None):
        self._db = db
        self.__id = dataset_id
        self.__name = dataset_name
        self.__category = category
        self.__source = source
        self.__last_updated = last_updated
        self.__record_count = record_count
        self.__file_size_mb = file_size_mb
        self.__created_at = created_at

    # Getters
    def get_id(self) -> int: return self.__id
    def get_name(self) -> str: return self.__name
    def get_category(self) -> str: return self.__category
    def get_source(self) -> str: return self.__source
    def get_last_updated(self) -> str: return self.__last_updated
    def get_record_count(self) -> int: return self.__record_count
    def get_file_size_mb(self) -> float: return self.__file_size_mb
    def get_created_at(self) -> str: return self.__created_at

    # Database methods
    def fetch_all(self) -> pd.DataFrame:
        """Fetch all datasets from the database."""
        query = "SELECT * FROM datasets_metadata"
        return self._db.fetch_dataframe(query)

    def get_all_datasets_df(self) -> pd.DataFrame:
        """Return all datasets as a pandas DataFrame."""
        return pd.DataFrame(self.fetch_all())

    # String representation
    def __str__(self) -> str:
        return (f"Dataset {self.__id}: {self.__name} "
                f"({self.__file_size_mb:.2f} MB, {self.__record_count} rows, Source: {self.__source})")