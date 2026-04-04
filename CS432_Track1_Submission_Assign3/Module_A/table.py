# table.py
from bplustree import BPlusTree

import pickle
import os


class Table:
    def __init__(self, name, schema, order=8, search_key=None, manager=None):
        self.name = name                        # Name of the table
        self.schema = schema                    # Table schema: dict of {column_name: data_type}
        self.order = order                      # Order of the B+ Tree (max number of children)
        self.data = BPlusTree(order=order)      # Underlying B+ Tree to store the data
        self.search_key = search_key            # Primary or search key used for indexing (must be in schema)
        self.manager = manager

    def validate_record(self, record):
        """
        Validate that the given record matches the table schema:
        - All required columns are present
        - Data types are correct
        """
        for col, dtype in self.schema.items():
            if col not in record:
                raise ValueError(f"Missing column '{col}' in record.")
            if not isinstance(record[col], dtype):
                raise TypeError(
                    f"Column '{col}' expects {dtype.__name__}, "
                    f"got {type(record[col]).__name__}."
                )
        return True

    def insert(self, record):
        """
        Insert a new record into the table.
        The record should be a dictionary matching the schema.
        The key used for insertion should be the value of the `search_key` field.
        Returns (True, key) on success, (False, error_message) on failure.
        """
        try:
            self.validate_record(record)
            key = record[self.search_key]

            # ATOMICITY: Record the insert in the journal
            if self.manager and self.manager.active_transaction is not None:
                self.manager.active_transaction.append((self, key, None, "INSERT"))
                self.manager._write_to_log("INSERT", self.name, key, record)

            self.data.insert(key, record)
            return (True, key)
        except (ValueError, TypeError) as e:
            return (False, str(e))

    def get(self, record_id):
        """
        Retrieve a single record by its ID (i.e., the value of the `search_key`).
        Returns (True, record) on success, (False, error_message) if not found.
        """
        result = self.data.search(record_id)
        if result is not None:
            return (True, result)
        return (False, f"Record with id '{record_id}' not found.")

    def get_all(self):
        """
        Retrieve all records stored in the table in sorted order by search key.
        Returns a list of (key, record) tuples.
        """
        return self.data.get_all()

    def update(self, record_id, new_record):
        """
        Update a record identified by `record_id` with `new_record` data.
        Returns (True, 'Record updated') on success, (False, error_message) on failure.
        """
        try:
            self.validate_record(new_record)
            # ATOMICITY: Fetch the OLD record before overwriting it
            success_get, old_record = self.get(record_id)
            if not success_get:
                return (False, f"Record with id '{record_id}' not found.")

            if self.manager and self.manager.active_transaction is not None:
                # Store the old_record so we can restore it during ROLLBACK
                self.manager.active_transaction.append((self, record_id, old_record, "UPDATE"))

            # Log old value for WAL recovery (UNDO needs it)
            if self.manager:
                self.manager._write_to_log("UPDATE", self.name, record_id, {
                    "old": old_record,
                    "new": new_record
                })

            self.data.update(record_id, new_record)
            return (True, "Record updated")
        except (ValueError, TypeError) as e:
            return (False, str(e))

    def delete(self, record_id):
        """
        Delete the record from the table by its `record_id`.
        Returns (True, 'Record deleted') on success, (False, error_message) on failure.
        """
        # ATOMICITY: Fetch the record before deleting it
        success_get, old_record = self.get(record_id)
        if not success_get:
            return (False, f"Record with id '{record_id}' not found.")

        if self.manager and self.manager.active_transaction is not None:
            # Store the old_record so we can re-insert it during ROLLBACK
            self.manager.active_transaction.append((self, record_id, old_record, "DELETE"))

        # Log old value for WAL recovery (UNDO needs it)
        if self.manager:
            self.manager._write_to_log("DELETE", self.name, record_id, old_record)

        success = self.data.delete(record_id)
        return (True, "Record deleted") if success else (False, "Deletion failed")

    def range_query(self, start_value, end_value):
        """
        Perform a range query using the search key.
        Returns records where start_value <= key <= end_value.
        Returns a list of (key, record) tuples.
        """
        return self.data.range_query(start_value, end_value)

    def visualize(self):
        """Visualize the underlying B+ Tree structure using Graphviz."""
        return self.data.visualize_tree()

    def __repr__(self):
        return (
            f"Table(name={self.name!r}, "
            f"schema={self.schema}, "
            f"search_key={self.search_key!r})"
        )
    
    def save_to_disk(self, directory="data"):
        """Saves the entire B+ Tree structure to a binary file."""
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        file_path = os.path.join(directory, f"{self.name}.tree")
        with open(file_path, 'wb') as f:
            pickle.dump(self.data, f)
        # print(f"Table '{self.name}' saved to {file_path}")

    def load_from_disk(self, directory="data"):
        """Loads the B+ Tree structure from a binary file if it exists."""
        file_path = os.path.join(directory, f"{self.name}.tree")
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                self.data = pickle.load(f)
            return True
        return False