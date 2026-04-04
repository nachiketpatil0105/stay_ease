from db_engine.bplustree import BPlusTree
import threading
import copy

class Table:
    def __init__(self, name, schema, order=8, search_key=None):
        self.name = name                        
        self.schema = schema                    
        self.order = order                      
        self.data = BPlusTree(order=order)      
        self.search_key = search_key            
        # NEW: Thread-safe lock for Isolation (ACID)
        self.lock = threading.RLock()

    def validate_record(self, record):
        for col, dtype in self.schema.items():
            if col not in record:
                raise ValueError(f"Missing column '{col}' in record.")
            if not isinstance(record[col], dtype):
                raise TypeError(f"Column '{col}' expects {dtype.__name__}, got {type(record[col]).__name__}.")
        return True

    def insert(self, record, tx_manager=None, tid=None):
        with self.lock: # Lock the table for this thread
            try:
                self.validate_record(record)
                key = record[self.search_key]
                
                # If a transaction manager is provided, log the action BEFORE modifying the tree
                if tx_manager and tid:
                    tx_manager.log_operation(tid, self.name, "INSERT", key, old_record=None, new_record=record)
                
                self.data.insert(key, record)
                return (True, key)
            except (ValueError, TypeError) as e:
                return (False, str(e))

    def update(self, record_id, new_record, tx_manager=None, tid=None):
        with self.lock: # Lock the table
            try:
                self.validate_record(new_record)
                
                # Fetch the old record so we can roll back if needed
                old_record = self.data.search(record_id)
                if old_record is None:
                    return (False, f"Record with id '{record_id}' not found.")
                
                # Log the change
                if tx_manager and tid:
                    tx_manager.log_operation(tid, self.name, "UPDATE", record_id, old_record=old_record, new_record=new_record)
                
                self.data.update(record_id, new_record)
                return (True, "Record updated")
            except (ValueError, TypeError) as e:
                return (False, str(e))

    def get(self, record_id):
        with self.lock: 
            result = self.data.search(record_id)
            if result is not None:
                # Give the user a snapshot, protecting the internal B+ Tree memory
                return (True, copy.deepcopy(result))
            return (False, f"Record with id '{record_id}' not found.")

    def get_all(self):
        with self.lock:
            # Protect the whole table dump
            return copy.deepcopy(self.data.get_all())

    def delete(self, record_id, tx_manager=None, tid=None):
        with self.lock:
            old_record = self.data.search(record_id)
            if old_record is None:
                return (False, f"Record with id '{record_id}' not found.")
                
            if tx_manager and tid:
                tx_manager.log_operation(tid, self.name, "DELETE", record_id, old_record=old_record, new_record=None)
                
            success = self.data.delete(record_id)
            if success:
                return (True, "Record deleted")
            return (False, "Delete failed internally")

    def range_query(self, start_value, end_value):
        with self.lock:
            return self.data.range_query(start_value, end_value)

    def visualize(self):
        return self.data.visualize_tree()

    def __repr__(self):
        return f"Table(name={self.name!r}, schema={self.schema}, search_key={self.search_key!r})"