from table import Table

class DatabaseManager:
    """
    The central registry for your DBMS.
    It manages multiple tables, ensuring they are easily accessible and organized.
    """
    
    def __init__(self, db_name="module_a_db"):
        """Initializes the database environment."""
        self.db_name = db_name
        # Dictionary to store our active tables in memory. 
        # Format: { 'table_name': Table_Object }
        self.tables = {}

    def create_table(self, table_name, columns, primary_key, btree_order=4):
        """
        Creates a new Table abstraction and registers it in the manager.
        
        Args:
            table_name (str): The name of the table.
            columns (list): A list of column names (e.g., ['id', 'name', 'age']).
            primary_key (str): The column to be used as the B+ Tree index key.
            btree_order (int): The order of the B+ Tree for this table.
            
        Returns:
            Table: The newly created Table object.
        """
        if table_name in self.tables:
            raise ValueError(f"Error: Table '{table_name}' already exists in database '{self.db_name}'.")
        
        # Initialize the Table (which internally initializes the BPlusTree)
        new_table = Table(
            name=table_name, 
            columns=columns, 
            primary_key=primary_key, 
            btree_order=btree_order
        )
        
        self.tables[table_name] = new_table
        return new_table

    def get_table(self, table_name):
        """
        Retrieves an existing table instance so you can run queries on it.
        """
        if table_name not in self.tables:
            raise ValueError(f"Error: Table '{table_name}' does not exist.")
            
        return self.tables[table_name]

    def drop_table(self, table_name):
        """
        Deletes a table and all its associated data/indexes from the database.
        """
        if table_name in self.tables:
            del self.tables[table_name]
            return True
        return False

    def show_tables(self):
        """
        Returns a list of all table names currently in the database.
        """
        return list(self.tables.keys())