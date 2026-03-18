# db_manager.py
from Database.table import Table


class DatabaseManager:
    """
    Manages multiple tables, acting as a lightweight database.
    Tables are stored in memory using B+ Tree indexing.
    """

    def __init__(self, name: str = "MyDatabase"):
        self.name   = name
        self.tables = {}  # table_name -> Table object

    def create_table(self, table_name: str, columns: list, order: int = 4):
        """
        Create a new table.
        Args:
            table_name : Name of the table
            columns    : List of column names (first = primary key)
            order      : B+ Tree order
        """
        if table_name in self.tables:
            print(f"Table '{table_name}' already exists.")
            return
        self.tables[table_name] = Table(table_name, columns, order)
        print(f"Table '{table_name}' created successfully.")

    def get_table(self, table_name: str) -> Table:
        """Get a table by name. Returns None if not found."""
        if table_name not in self.tables:
            print(f"Table '{table_name}' does not exist.")
            return None
        return self.tables[table_name]

    def drop_table(self, table_name: str):
        """Delete a table entirely."""
        if table_name in self.tables:
            del self.tables[table_name]
            print(f"Table '{table_name}' dropped.")
        else:
            print(f"Table '{table_name}' does not exist.")

    def list_tables(self) -> list:
        """Return list of all table names."""
        return list(self.tables.keys())

    def __repr__(self):
        return f"DatabaseManager(name={self.name}, tables={self.list_tables()})"