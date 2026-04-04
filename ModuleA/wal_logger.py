# wal_logger.py
import json
import os
import time

class WALLogger:
    """
    Write-Ahead Logger.
    Every operation is written to disk BEFORE it touches the B+ Tree.
    This is the crash-recovery foundation.
    
    Log format (one JSON object per line):
    {"txn_id": 1, "lsn": 0, "type": "BEGIN", ...}
    {"txn_id": 1, "lsn": 1, "type": "WRITE", "table": "users", 
     "operation": "INSERT", "key": 1, "old_value": null, "new_value": {...}}
    {"txn_id": 1, "lsn": 2, "type": "COMMIT"}
    """
    
    def __init__(self, log_file="wal.log"):
        self.log_file = log_file
        self.lsn = 0  # Log Sequence Number — every entry gets a unique, increasing number
        self._load_lsn()
    
    def _load_lsn(self):
        """On restart, find the highest LSN so we don't repeat numbers."""
        if not os.path.exists(self.log_file):
            self.lsn = 0
            return
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entry = json.loads(line)
                        self.lsn = max(self.lsn, entry.get("lsn", 0) + 1)
        except (json.JSONDecodeError, IOError):
            self.lsn = 0
    
    def _write(self, entry: dict):
        """Append a single log entry to disk. Flush immediately — no buffering!"""
        entry["lsn"] = self.lsn
        entry["timestamp"] = time.time()
        self.lsn += 1
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
            f.flush()           # Push from Python buffer to OS
            os.fsync(f.fileno()) # Push from OS buffer to actual disk
    
    def log_begin(self, txn_id):
        """Record that a transaction has started."""
        self._write({
            "txn_id": txn_id,
            "type": "BEGIN"
        })
    
    def log_write(self, txn_id, table_name, operation, key, old_value, new_value):
        """
        Record a data modification BEFORE applying it to the B+ Tree.
        old_value is crucial — it's what we use to UNDO the operation on rollback.
        operation: "INSERT", "UPDATE", or "DELETE"
        """
        self._write({
            "txn_id": txn_id,
            "type": "WRITE",
            "table": table_name,
            "operation": operation,
            "key": key,
            "old_value": old_value,   # None for INSERT (nothing existed before)
            "new_value": new_value    # None for DELETE (nothing exists after)
        })
    
    def log_commit(self, txn_id):
        """Record that a transaction has successfully completed."""
        self._write({
            "txn_id": txn_id,
            "type": "COMMIT"
        })
    
    def log_rollback(self, txn_id):
        """Record that a transaction was explicitly aborted."""
        self._write({
            "txn_id": txn_id,
            "type": "ROLLBACK"
        })
    
    def read_log(self):
        """Read all log entries from disk. Used during crash recovery."""
        entries = []
        if not os.path.exists(self.log_file):
            return entries
        with open(self.log_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        # Corrupted line from a crash mid-write — safely ignore
                        pass
        return entries
    
    def clear_log(self):
        """Wipe the log. Call this after a clean checkpoint (optional)."""
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        self.lsn = 0