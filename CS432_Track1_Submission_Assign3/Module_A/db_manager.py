# db_manager.py
from table import Table
import json
import os
import threading


class DatabaseManager:
    def __init__(self):
        self.databases = {}  # Dictionary to store databases as {db_name: {table_name: Table instance}}
        self.active_transaction = None
        self.log_file = "stayease_wal.log"
        self.lock = threading.Lock()

    def create_database(self, db_name):
        """
        Create a new database with the given name.
        Returns (True, message) on success, (False, message) if already exists.
        """
        if db_name in self.databases:
            return (False, f"Database '{db_name}' already exists.")
        self.databases[db_name] = {}
        return (True, f"Database '{db_name}' created successfully")

    def delete_database(self, db_name):
        """
        Delete an existing database and all its tables.
        Returns (True, message) on success, (False, message) if not found.
        """
        if db_name not in self.databases:
            return (False, f"Database '{db_name}' does not exist.")
        del self.databases[db_name]
        return (True, f"Database '{db_name}' deleted successfully.")

    def list_databases(self):
        """
        Return a list of all database names currently managed.
        """
        return list(self.databases.keys())

    def create_table(self, db_name, table_name, schema, order=8, search_key=None):
        """
        Create a new table within a specified database.
        Returns (True, message) on success, (False, message) on failure.
        """
        if db_name not in self.databases:
            return (False, f"Database '{db_name}' does not exist. Create it first.")
        if table_name in self.databases[db_name]:
            return (False, f"Table '{table_name}' already exists in database '{db_name}'.")
        self.databases[db_name][table_name] = Table(
            name=table_name,
            schema=schema,
            order=order,
            search_key=search_key,
            manager=self 
        )
        return (True, f"Table '{table_name}' created successfully in database '{db_name}'")

    def delete_table(self, db_name, table_name):
        """
        Delete a table from the specified database.
        Returns (True, message) on success, (False, message) on failure.
        """
        if db_name not in self.databases:
            return (False, f"Database '{db_name}' does not exist.")
        if table_name not in self.databases[db_name]:
            return (False, f"Table '{table_name}' does not exist in database '{db_name}'.")
        del self.databases[db_name][table_name]
        return (True, f"Table '{table_name}' deleted from database '{db_name}'.")

    def list_tables(self, db_name):
        """
        List all tables within a given database.
        Returns (table_names_list, message).
        """
        if db_name not in self.databases:
            return ([], f"Database '{db_name}' does not exist.")
        tables = list(self.databases[db_name].keys())
        return (tables, f"Tables in '{db_name}': {tables}")

    def get_table(self, db_name, table_name):
        """
        Retrieve a Table instance from a given database.
        Returns (Table, message) on success, (None, message) on failure.
        """
        if db_name not in self.databases:
            return (None, f"Database '{db_name}' does not exist.")
        if table_name not in self.databases[db_name]:
            return (None, f"Table '{table_name}' does not exist in database '{db_name}'.")
        table = self.databases[db_name][table_name]
        return (table, f"Table '{table_name}' retrieved successfully.")

    def __repr__(self):
        db_summary = {db: list(tables.keys()) for db, tables in self.databases.items()}
        return f"DatabaseManager(databases={db_summary})"
    
    def persist_all(self, db_name):
        """Triggers a save for every table in the specified database."""
        if db_name in self.databases:
            for table_obj in self.databases[db_name].values():
                table_obj.save_to_disk()
            print(f"All tables in '{db_name}' persisted to disk.")

    def reload_all(self, db_name):
        """Restores all tables from disk on startup."""
        if db_name in self.databases:
            for table_obj in self.databases[db_name].values():
                if table_obj.load_from_disk():
                    print(f"Restored table '{table_obj.name}' from disk.")

    def _write_to_log(self, op_type, table_name, key, data):
        log_entry = {
            "op": op_type,
            "table": table_name,
            "key": key,
            "data": data
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def begin(self):
        """Starts a new transaction block."""
        self.lock.acquire()
            
        self.active_transaction = []
        self._write_to_log("BEGIN", None, None, None)
        print("BEGIN: Transaction started.")
        return True
    
    def rollback(self):
        """
        Reverts all changes made during the current active transaction.
        Iterates through the journal in reverse to undo operations.
        """
        if self.active_transaction is None:
            print("No active transaction to rollback.")
            return False

        try:
            # Undo operations in reverse order (Last-In, First-Out) 
            for table_obj, key, old_value, op_type in reversed(self.active_transaction):
                if op_type == "INSERT":
                    # To undo an insert, we delete the new record
                    if table_obj.data.search(key) is not None:
                        table_obj.data.delete(key)
                elif op_type == "UPDATE":
                    # To undo an update, we restore the previous version of the record
                    table_obj.data.update(key, old_value)
                elif op_type == "DELETE":
                    # To undo a delete, we re-insert the original record
                    table_obj.data.insert(key, old_value)
        finally:
            self.active_transaction = None # Clear the transaction state 
            self.lock.release()
                
        print("ROLLBACK: All changes reverted. Database is back to original state[cite: 74, 118].")
        return True
    
    def commit(self, db_name):
        """
        Finalizes the transaction and persists changes to disk[cite: 67, 84, 96].
        """
        if self.active_transaction is None:
            print("No active transaction to commit.")
            return False

        # Since the B+ Trees were updated in real-time, we just need to 
        # persist the current state to the .tree files.
        try:
            self._write_to_log("COMMIT", None, None, None)
            self.persist_all(db_name)
            print("COMMIT: Changes saved.")
        finally:
            self.active_transaction = None
            self.lock.release() # Release lock so others can use the DB
            print("LOCK RELEASED.")
        return True
    
    def recover(self, db_name):
        """
        Scans the WAL log to restore the database to a consistent state.
        Fulfills: 'Retain committed transactions' and 'Undo incomplete'.
        """
        if not os.path.exists(self.log_file):
            return

        print(f"--- RECOVERY: Processing {self.log_file} ---")

        with open(self.log_file, "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        if not lines:
            return

        # Parse all log entries
        entries = []
        for line in lines:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

        # Split into transactions by BEGIN/COMMIT boundaries
        transactions = []
        current_tx = []
        in_tx = False

        for entry in entries:
            if entry["op"] == "BEGIN":
                current_tx = []
                in_tx = True
            elif entry["op"] == "COMMIT":
                if in_tx:
                    transactions.append(("COMMITTED", current_tx))
                current_tx = []
                in_tx = False
            else:
                if in_tx:
                    current_tx.append(entry)

        # If there are ops after last BEGIN with no COMMIT — incomplete transaction
        if in_tx and current_tx:
            transactions.append(("INCOMPLETE", current_tx))

        # Process each transaction
        for status, ops in transactions:
            if status == "COMMITTED":
                # Redo: replay all ops from this committed transaction
                print("RECOVERY: Replaying committed transaction...")
                for entry in ops:
                    table_obj, _ = self.get_table(db_name, entry["table"])
                    if table_obj is None:
                        continue
                    op = entry["op"]
                    key = entry["key"]
                    data = entry["data"]

                    if op == "INSERT":
                        # Only insert if not already present (pickle may have it)
                        if table_obj.data.search(key) is None:
                            table_obj.data.insert(key, data)
                            print(f"  REDO INSERT: {entry['table']} key={key}")

                    elif op == "UPDATE":
                        if table_obj.data.search(key) is not None:
                            table_obj.data.update(key, data["new"])
                            print(f"  REDO UPDATE: {entry['table']} key={key}")

                    elif op == "DELETE":
                        if table_obj.data.search(key) is not None:
                            table_obj.data.delete(key)
                            print(f"  REDO DELETE: {entry['table']} key={key}")

            elif status == "INCOMPLETE":
                # Undo: incomplete transaction — ignore, data not committed
                print("RECOVERY: Incomplete transaction found. Ignoring partial updates.")
                for entry in ops:
                    table_obj, _ = self.get_table(db_name, entry["table"])
                    if table_obj is None:
                        continue
                    op = entry["op"]
                    key = entry["key"]
                    data = entry["data"]

                    # If an incomplete INSERT made it to disk, remove it
                    if op == "INSERT":
                        if table_obj.data.search(key) is not None:
                            table_obj.data.delete(key)
                            print(f"  UNDO INSERT: {entry['table']} key={key}")

                    # If an incomplete UPDATE made it to disk, restore old value
                    elif op == "UPDATE":
                        if data is not None and table_obj.data.search(key) is not None:
                            table_obj.data.update(key, data["old"])
                            print(f"  UNDO UPDATE: {entry['table']} key={key}")

                    # If an incomplete DELETE made it to disk, re-insert
                    elif op == "DELETE":
                        if data is not None and table_obj.data.search(key) is None:
                            table_obj.data.insert(key, data)
                            print(f"  UNDO DELETE: {entry['table']} key={key}")

        # After recovery, clear the log because the state is now synced
        open(self.log_file, 'w').close()
        print("RECOVERY: Log cleared. Database state is consistent.")