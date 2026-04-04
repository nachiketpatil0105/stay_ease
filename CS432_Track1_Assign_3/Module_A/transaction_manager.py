import json
import os
import threading
import time
import uuid

class TransactionManager:
    def __init__(self):
        self.active_transaction = None
        self.log_file = "stayease_wal.log"
        self.lock = threading.Lock()
        self._current_tx_id = None

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
            "tx_id": self._current_tx_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
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
            
        self._current_tx_id = str(uuid.uuid4())[:8]
        self.active_transaction = []
        self._write_to_log("BEGIN", None, None, None)
        print(f"BEGIN: Transaction started. [tx_id={self._current_tx_id}]")
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

            # Clean up log — remove the incomplete transaction, keep committed ones
            if os.path.exists(self.log_file):
                with open(self.log_file, "r") as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]
                entries = []
                for line in lines:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
                # Rewrite only committed transactions
                committed_blocks = []
                current_tx = []
                in_tx = False
                for entry in entries:
                    if entry["op"] == "BEGIN":
                        current_tx = []
                        in_tx = True
                    elif entry["op"] == "COMMIT":
                        if in_tx:
                            committed_blocks.append(current_tx)
                        current_tx = []
                        in_tx = False
                    else:
                        if in_tx:
                            current_tx.append(entry)
                with open(self.log_file, "w") as f:
                    for block in committed_blocks:
                        tx_id = block[0]["tx_id"] if block else "unknown"
                        f.write(json.dumps({"tx_id": tx_id, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "op": "BEGIN", "table": None, "key": None, "data": None}) + "\n")
                        for entry in block:
                            f.write(json.dumps(entry) + "\n")
                        f.write(json.dumps({"tx_id": tx_id, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "op": "COMMIT", "table": None, "key": None, "data": None}) + "\n")

            self.lock.release()
                
        print("ROLLBACK: All changes reverted. Database is back to original state.")
        return True
    
    def commit(self, db_name):
        """
        Finalizes the transaction and persists changes to disk.
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
            self._current_tx_id = None
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

        # After recovery, rewrite log keeping only committed transactions
        # Remove incomplete transactions, retain committed ones for future recovery
        with open(self.log_file, 'w') as f:
            for status, ops in transactions:
                if status == "COMMITTED":
                    tx_id = ops[0]["tx_id"] if ops else "unknown"
                    f.write(json.dumps({"tx_id": tx_id, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "op": "BEGIN", "table": None, "key": None, "data": None}) + "\n")
                    for entry in ops:
                        f.write(json.dumps(entry) + "\n")
                    f.write(json.dumps({"tx_id": tx_id, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "op": "COMMIT", "table": None, "key": None, "data": None}) + "\n")
        print("RECOVERY: Incomplete transactions removed. Committed transactions retained in log.")