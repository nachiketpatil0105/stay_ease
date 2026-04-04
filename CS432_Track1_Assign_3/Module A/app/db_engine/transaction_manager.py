import os
import json
import threading
from datetime import datetime

class TransactionManager:
    def __init__(self, db_manager, log_file="stayease_wal.log"):
        self.db = db_manager
        self.log_file = log_file
        self.active_transactions = {}
        # A global lock to ensure WAL writes don't overlap during stress testing
        self.wal_lock = threading.Lock()
        self.transaction_counter = 1
        
        # The Master Lock for Serialized Execution
        self.serial_lock = threading.RLock()

    def begin_transaction(self):
        """Starts a new transaction and locks the database."""
        self.serial_lock.acquire() # <-- Master lock acquired here!
        
        tid = f"TXN-{self.transaction_counter}-{datetime.now().strftime('%H%M%S%f')}"
        self.transaction_counter += 1
        
        self.active_transactions[tid] = {
            "status": "IN_PROGRESS",
            "operations": [] # Keeps track of old values for rollback
        }
        self._write_to_wal(tid, "BEGIN", {})
        return tid

    def log_operation(self, tid, table_name, action, key, old_record, new_record):
        """Logs an operation to memory (for rollback) and disk (for durability)."""
        if tid not in self.active_transactions:
            raise ValueError(f"Transaction {tid} is not active.")

        # Save to memory for quick rollback
        self.active_transactions[tid]["operations"].append({
            "table": table_name,
            "action": action, # 'INSERT', 'UPDATE', 'DELETE'
            "key": key,
            "old_record": old_record,
            "new_record": new_record
        })

        # Save to disk for crash recovery (Write-Ahead Logging)
        wal_entry = {
            "table": table_name,
            "action": action,
            "key": key,
            "old_record": old_record,
            "new_record": new_record
        }
        self._write_to_wal(tid, action, wal_entry)

    def commit(self, tid):
        """Commits a transaction permanently."""
        if tid not in self.active_transactions:
            self.serial_lock.release() # Release lock safely if error occurs
            raise ValueError(f"Transaction {tid} is not active.")
            
        self._write_to_wal(tid, "COMMIT", {})
        del self.active_transactions[tid]
        
        self.serial_lock.release() # <-- Unlock the database for the next user!
        return True

    def rollback(self, tid):
        """Undoes all operations within an incomplete transaction."""
        if tid not in self.active_transactions:
            self.serial_lock.release() # Release lock safely if error occurs
            return False

        print(f"\n[ROLLBACK] Initiating rollback for {tid}...")
        
        # We must undo operations in REVERSE order
        operations = reversed(self.active_transactions[tid]["operations"])
        
        for op in operations:
            table_name = op["table"]
            table_instance = self.db.databases['stayease'][table_name] # Assuming DB is 'stayease'
            
            if op["action"] == "INSERT":
                # To undo an insert, we delete the record
                table_instance.data.delete(op["key"])
                print(f"  -> Undid INSERT on {table_name} (Key: {op['key']})")
                
            elif op["action"] == "UPDATE":
                # To undo an update, we restore the old record
                table_instance.data.update(op["key"], op["old_record"])
                print(f"  -> Undid UPDATE on {table_name} (Key: {op['key']})")
                
            elif op["action"] == "DELETE":
                # To undo a delete, we re-insert the old record
                table_instance.data.insert(op["key"], op["old_record"])
                print(f"  -> Undid DELETE on {table_name} (Key: {op['key']})")

        self._write_to_wal(tid, "ROLLBACK", {})
        del self.active_transactions[tid]
        print(f"[ROLLBACK] {tid} successfully aborted.\n")
        
        self.serial_lock.release()  #Unlock the database so others can use it
        return True

    def _write_to_wal(self, tid, action, data):
        """Writes a serialized log entry to the disk sequentially."""
        log_entry = json.dumps({
            "timestamp": str(datetime.now()),
            "tid": tid,
            "action": action,
            "data": data
        })
        with self.wal_lock:
            with open(self.log_file, "a") as f:
                f.write(log_entry + "\n")
    
    def recover(self):
        """Reads the WAL on startup and rolls back any incomplete transactions."""
        if not os.path.exists(self.log_file):
            return # No log file means it's a fresh database

        print("\n[RECOVERY] Scanning Write-Ahead Log for incomplete transactions...")
        uncommitted_txns = {}

        # 1. Read the log to find out who finished and who didn't
        with open(self.log_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    tid = entry["tid"]
                    action = entry["action"]

                    if action == "BEGIN":
                        uncommitted_txns[tid] = []
                    elif action in ["INSERT", "UPDATE", "DELETE"]:
                        if tid in uncommitted_txns:
                            uncommitted_txns[tid].append(entry["data"])
                    elif action in ["COMMIT", "ROLLBACK"]:
                        if tid in uncommitted_txns:
                            del uncommitted_txns[tid] # Transaction resolved safely
                except json.JSONDecodeError:
                    continue # Skip corrupted lines

        # 2. Rollback the ones that got stuck in limbo!
        if not uncommitted_txns:
            print("[RECOVERY] All past transactions were resolved safely. System is clean.\n")
            return

        print(f"[RECOVERY] Found {len(uncommitted_txns)} crashed transaction(s). Cleaning up...")
        for tid, operations in uncommitted_txns.items():
            # Reverse order to safely walk backward
            for op in reversed(operations):
                table_name = op["table"]
                if table_name not in self.db.databases.get('stayease', {}):
                    continue
                    
                table_instance = self.db.databases['stayease'][table_name]
                
                # Apply the exact opposite of what the crashed transaction tried to do
                if op["action"] == "INSERT":
                    table_instance.data.delete(op["key"])
                elif op["action"] == "UPDATE":
                    table_instance.data.update(op["key"], op["old_record"])
                elif op["action"] == "DELETE":
                    table_instance.data.insert(op["key"], op["old_record"])
                    
            # Write a rollback entry to the log so we don't try to recover it again
            self._write_to_wal(tid, "RECOVERED_ROLLBACK", {})
            print(f"[RECOVERY] Successfully reversed {tid}.")
            
        print("[RECOVERY] Database is now in a consistent state.\n")
        

