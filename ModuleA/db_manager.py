# db_manager.py
from table import Table

class DatabaseManager:
    def __init__(self):
        self.databases = {}  # Dictionary to store databases as {db_name: {table_name: Table instance}}

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
            search_key=search_key
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

    def save_to_disk(self, snapshot_file="db_snapshot.pkl"):
        """
        Persist the entire in-memory state (all databases + all B+ Trees)
        to a single pickle snapshot.  Called automatically on every COMMIT
        by the TransactionManager.
        """
        import pickle, os
        backup = snapshot_file + ".bak"
        try:
            # Write to a temp file first so a crash mid-write can't corrupt
            # the existing snapshot.
            with open(backup, "wb") as f:
                pickle.dump(self.databases, f)
            os.replace(backup, snapshot_file)   # Atomic rename
            print(f"[Persistence] Snapshot saved → '{snapshot_file}'")
        except Exception as e:
            print(f"[Persistence] ERROR saving snapshot: {e}")
            raise

    def load_from_disk(self, snapshot_file="db_snapshot.pkl"):
        """
        Restore the database state from a snapshot file.
        Returns True if data was loaded, False if no snapshot exists yet.
        Called once at startup before crash recovery runs.
        """
        import pickle, os
        if not os.path.exists(snapshot_file):
            print("[Persistence] No snapshot found — starting with empty database.")
            return False
        try:
            with open(snapshot_file, "rb") as f:
                self.databases = pickle.load(f)
            print(f"[Persistence] State restored ← '{snapshot_file}'")
            return True
        except Exception as e:
            print(f"[Persistence] ERROR loading snapshot: {e}")
            return False

    def __repr__(self):
        db_summary = {db: list(tables.keys()) for db, tables in self.databases.items()}
        return f"DatabaseManager(databases={db_summary})"