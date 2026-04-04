from db_engine.table import Table


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

    def __repr__(self):
        db_summary = {db: list(tables.keys()) for db, tables in self.databases.items()}
        return f"DatabaseManager(databases={db_summary})"