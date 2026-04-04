# persistence.py
import pickle
import os

class Persistence:
    """
    Saves and loads the entire DatabaseManager state to/from disk.
    Called after every COMMIT to ensure durability.
    
    We use pickle for simplicity — it serializes the entire Python object graph,
    which includes all B+ Tree nodes and their data.
    """
    
    def __init__(self, snapshot_file="db_snapshot.pkl"):
        self.snapshot_file = snapshot_file
        self.backup_file   = snapshot_file + ".bak"
    
    def save(self, db_manager):
        """
        Save database state to disk using atomic write:
        1. Write to a temp backup file
        2. Rename it to the real file (rename is atomic on most OS)
        This prevents a half-written snapshot from corrupting your data.
        """
        try:
            # Write to backup first
            with open(self.backup_file, 'wb') as f:
                pickle.dump(db_manager.databases, f)
            
            # Atomically replace the old snapshot
            os.replace(self.backup_file, self.snapshot_file)
            print(f"[Persistence] Snapshot saved to '{self.snapshot_file}'")
        except Exception as e:
            print(f"[Persistence] ERROR saving snapshot: {e}")
            raise
    
    def load(self, db_manager):
        """
        Restore database state from the snapshot file.
        Returns True if data was loaded, False if no snapshot exists.
        """
        if not os.path.exists(self.snapshot_file):
            print("[Persistence] No snapshot found — starting fresh.")
            return False
        
        try:
            with open(self.snapshot_file, 'rb') as f:
                db_manager.databases = pickle.load(f)
            print(f"[Persistence] State restored from '{self.snapshot_file}'")
            return True
        except Exception as e:
            print(f"[Persistence] ERROR loading snapshot: {e}")
            return False