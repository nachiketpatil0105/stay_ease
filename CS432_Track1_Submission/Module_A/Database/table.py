# table.py
from Database.bplustree import BPlusTree


class Table:
    """
    A table abstraction that uses a B+ Tree as its index.
    Each record is stored as a dictionary of column:value pairs.
    The first column is used as the key for the B+ Tree.
    """

    def __init__(self, name: str, columns: list, order: int = 4):
        """
        Args:
            name    : Table name
            columns : List of column names (first column = primary key)
            order   : B+ Tree order
        """
        self.name    = name
        self.columns = columns
        self.tree    = BPlusTree(order=order)

    # ------------------------------------------------------------------ #

    def insert(self, record: dict):
        """
        Insert a record into the table.
        record must contain all columns.
        First column value is used as the key.
        """
        key = record[self.columns[0]]
        self.tree.insert(key, record)

    def search(self, key):
        """Search for a record by primary key. Returns record or None."""
        return self.tree.search(key)

    def update(self, key, updated_record: dict):
        """Update a record by primary key. Returns True if successful."""
        return self.tree.update(key, updated_record)

    def delete(self, key):
        """Delete a record by primary key. Returns True if successful."""
        return self.tree.delete(key)

    def range_query(self, start_key, end_key) -> list:
        """Return all records where start_key <= key <= end_key."""
        return self.tree.range_query(start_key, end_key)

    def get_all(self) -> list:
        """Return all records in sorted order by primary key."""
        return self.tree.get_all()

    def visualize(self):
        """Visualize the underlying B+ Tree structure."""
        return self.tree.visualize_tree()

    def __repr__(self):
        return f"Table(name={self.name}, columns={self.columns}, records={len(self.tree)})"