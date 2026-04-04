# transaction.py
import time

class TransactionState:
    ACTIVE    = "ACTIVE"
    COMMITTED = "COMMITTED"
    ABORTED   = "ABORTED"

class Transaction:
    """
    Represents a single database transaction.
    
    Keeps an undo log — a list of operations in reverse order.
    If rollback is needed, we replay the undo log backwards.
    """
    
    _id_counter = 0  # Simple global counter for unique IDs
    
    def __init__(self):
        Transaction._id_counter += 1
        self.txn_id    = Transaction._id_counter
        self.state     = TransactionState.ACTIVE
        self.undo_log  = []   # Stack of (table_name, operation, key, old_value)
        self.start_time = time.time()
    
    def record_operation(self, table_name, operation, key, old_value):
        """
        Store enough info to UNDO this one operation later.
        
        For INSERT:  old_value = None  → undo by DELETE
        For DELETE:  old_value = <record> → undo by INSERT
        For UPDATE:  old_value = <old record> → undo by UPDATE back to old
        """
        self.undo_log.append({
            "table":     table_name,
            "operation": operation,   # original operation, not the undo
            "key":       key,
            "old_value": old_value
        })
    
    def get_undo_steps(self):
        """
        Return undo steps in REVERSE order.
        The last thing we did must be undone first (LIFO).
        """
        return list(reversed(self.undo_log))
    
    def __repr__(self):
        return (f"Transaction(id={self.txn_id}, "
                f"state={self.state}, "
                f"ops={len(self.undo_log)})")