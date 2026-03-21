from bplustree import BPlusTree

class Table:
    """
    Represents a single database table. 
    It manages the schema (columns) and uses a B+ Tree as its primary storage engine.
    """
    def __init__(self, name, columns, primary_key, btree_order=4):
        self.name = name
        self.columns = columns  # A list of expected column names, e.g., ['id', 'name', 'role']
        self.primary_key = primary_key
        
        if primary_key not in columns:
            raise ValueError(f"Primary key '{primary_key}' must be one of the defined columns.")
            
        # Initialize the core indexing engine for this specific table
        self.index = BPlusTree(order=btree_order)

    def insert(self, record):
        """
        Inserts a new record (dictionary) into the table.
        """
        # Validate the record structure
        if self.primary_key not in record:
            raise ValueError(f"Record is missing the primary key '{self.primary_key}'.")
            
        pk_value = record[self.primary_key]
        
        # Enforce Primary Key uniqueness (like a real SQL database)
        if self.index.search(pk_value) is not None:
            print(f"Insert Error: Record with {self.primary_key} = {pk_value} already exists.")
            return False
            
        # Store the entire record dictionary as the "value" in the B+ Tree
        self.index.insert(pk_value, record)
        return True

    def select(self, pk_value):
        """
        Retrieves a single record by its primary key using an exact match search.
        """
        return self.index.search(pk_value)

    def update(self, pk_value, updated_fields):
        """
        Updates specific fields in an existing record.
        """
        # Fetch the existing record
        existing_record = self.index.search(pk_value)
        if existing_record is None:
            print(f"Update Error: No record found with {self.primary_key} = {pk_value}.")
            return False
            
        # Apply the updates to the dictionary
        for column, new_val in updated_fields.items():
            if column in self.columns:
                existing_record[column] = new_val
            else:
                print(f"Warning: Column '{column}' does not exist in table schema. Ignoring.")
                
        # Save it back to the tree
        return self.index.update(pk_value, existing_record)

    def delete(self, pk_value):
        """
        Removes a record from the table based on its primary key.
        """
        success = self.index.delete(pk_value)
        if not success:
            print(f"Delete Error: No record found with {self.primary_key} = {pk_value}.")
        return success

    def range_query(self, start_pk, end_pk):
        """
        Retrieves all records where the primary key falls within the specified range.
        Takes advantage of the B+ tree's efficient leaf-node linked list.
        """
        # The B+ tree returns a list of tuples: [(key, value), (key, value)]
        # We only want to return the actual record dictionaries (the values)
        results = self.index.range_query(start_pk, end_pk)
        return [record for key, record in results]

    def select_all(self):
        """
        Retrieves every record currently stored in the table.
        """
        results = self.index.get_all()
        return [record for key, record in results]