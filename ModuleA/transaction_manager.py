# transaction_manager.py
import threading
from transaction import Transaction, TransactionState
from wal_logger import WALLogger

class TransactionManager:
    """
    Coordinates transactions across multiple B+ Tree tables.
    Works with your Table class which exposes its B+ Tree as self.data
    """

    def __init__(self, db_manager, db_name, log_file="wal.log"):
        self.db_manager   = db_manager
        self.db_name      = db_name
        self.logger       = WALLogger(log_file)
        self.active_txns  = {}
        self.table_locks  = {}   # {table_name: threading.Lock()}
        self.lock_owners  = {}   # {table_name: txn_id}
        self._mgr_lock    = threading.Lock()

        # Run crash recovery on every startup
        self._recover()

    # ------------------------------------------------------------------ #
    #  INTERNAL HELPERS                                                    #
    # ------------------------------------------------------------------ #

    def _get_table(self, table_name):
        """
        Retrieve the Table object from the DatabaseManager.
        Raises RuntimeError if the table doesn't exist.
        """
        table, msg = self.db_manager.get_table(self.db_name, table_name)
        if table is None:
            raise RuntimeError(msg)
        return table

    def _check_active(self, txn):
        """Guard: reject operations on committed or aborted transactions."""
        if txn.state != TransactionState.ACTIVE:
            raise RuntimeError(
                f"Transaction {txn.txn_id} is {txn.state} — cannot perform operations."
            )

    # ------------------------------------------------------------------ #
    #  LOCK MANAGEMENT                                                     #
    # ------------------------------------------------------------------ #

    def _get_lock(self, table_name):
        """Get (or lazily create) the threading.Lock for a table."""
        with self._mgr_lock:
            if table_name not in self.table_locks:
                self.table_locks[table_name] = threading.Lock()
            return self.table_locks[table_name]

    def _acquire_lock(self, txn, table_name):
        """
        Acquire a write lock on a table for this transaction.
        Re-entrant: if this transaction already holds the lock, skip.
        Blocks until the lock is free (held by another transaction).
        """
        if self.lock_owners.get(table_name) == txn.txn_id:
            return  # Already own it

        lock = self._get_lock(table_name)
        lock.acquire()  # Blocks if another transaction holds it
        self.lock_owners[table_name] = txn.txn_id

    def _release_all_locks(self, txn):
        """Release every lock this transaction holds. Call on commit or rollback."""
        with self._mgr_lock:
            held = [t for t, owner in self.lock_owners.items()
                    if owner == txn.txn_id]

        for table_name in held:
            lock = self._get_lock(table_name)
            del self.lock_owners[table_name]
            try:
                lock.release()
            except RuntimeError:
                pass  # Already released

    # ------------------------------------------------------------------ #
    #  TRANSACTION LIFECYCLE                                               #
    # ------------------------------------------------------------------ #

    def begin_transaction(self):
        """
        Start a new transaction.
        Returns a Transaction object — pass it into every operation.
        """
        txn = Transaction()
        self.active_txns[txn.txn_id] = txn
        self.logger.log_begin(txn.txn_id)
        print(f"[TXN {txn.txn_id}] BEGIN")
        return txn

    def commit(self, txn):
        """
        Commit a transaction:
        1. Write COMMIT to the WAL (point of no return)
        2. Save full DB state to disk  (durability)
        3. Release all locks
        """
        self._check_active(txn)

        self.logger.log_commit(txn.txn_id)   # WAL commit record first
        self.db_manager.save_to_disk()        # Flush to snapshot

        txn.state = TransactionState.COMMITTED
        self._release_all_locks(txn)
        del self.active_txns[txn.txn_id]

        print(f"[TXN {txn.txn_id}] COMMIT — {len(txn.undo_log)} op(s) persisted")
        return True

    def rollback(self, txn):
        """
        Rollback a transaction:
        1. Undo every operation in reverse order (LIFO)
        2. Write ROLLBACK to the WAL
        3. Release all locks
        """
        self._check_active(txn)

        print(f"[TXN {txn.txn_id}] ROLLBACK — undoing {len(txn.undo_log)} op(s)...")

        for step in txn.get_undo_steps():   # Reversed order
            self._apply_undo(step)

        self.logger.log_rollback(txn.txn_id)
        txn.state = TransactionState.ABORTED
        self._release_all_locks(txn)
        del self.active_txns[txn.txn_id]

        print(f"[TXN {txn.txn_id}] ROLLBACK complete")
        return True

    # ------------------------------------------------------------------ #
    #  UNDO ENGINE                                                         #
    # ------------------------------------------------------------------ #

    def _apply_undo(self, step):
        """
        Reverse a single operation directly on the B+ Tree (self.data).
        This is called both during explicit rollback AND crash recovery.

        Undo logic:
            original INSERT  → DELETE  the key
            original DELETE  → INSERT  the old record back
            original UPDATE  → UPDATE  back to the old value
        """
        table      = self._get_table(step["table"])
        op         = step["operation"]
        key        = step["key"]
        old_value  = step["old_value"]

        if op == "INSERT":
            # We inserted something that shouldn't exist — remove it
            table.data.delete(key)
            print(f"  ↩ Undo INSERT on '{step['table']}': deleted key={key}")

        elif op == "DELETE":
            # We deleted something — put it back
            table.data.insert(key, old_value)
            print(f"  ↩ Undo DELETE on '{step['table']}': restored key={key} → {old_value}")

        elif op == "UPDATE":
            # We changed a value — restore the previous one
            table.data.update(key, old_value)
            print(f"  ↩ Undo UPDATE on '{step['table']}': key={key} restored → {old_value}")

    # ------------------------------------------------------------------ #
    #  TRANSACTIONAL CRUD                                                  #
    # ------------------------------------------------------------------ #
    # Always use these instead of calling table.data directly.
    # Pattern for every write:
    #   1. Check transaction is active
    #   2. Acquire table lock
    #   3. Read current state (for undo image)
    #   4. Write to WAL BEFORE touching the tree
    #   5. Apply to B+ Tree (table.data)
    #   6. Record undo info in the transaction object

    def insert(self, txn, table_name, key, value):
        """
        Transactional insert.
        If the key already exists, it behaves as an upsert (like your B+ Tree does).
        """
        self._check_active(txn)
        self._acquire_lock(txn, table_name)

        table = self._get_table(table_name)

        # Capture whatever is currently there (None if brand new key)
        existing = table.data.search(key)

        # WAL first — before any data change
        self.logger.log_write(
            txn.txn_id, table_name, "INSERT", key, existing, value
        )

        # Apply to B+ Tree
        table.data.insert(key, value)

        # Save enough info to undo this step
        txn.record_operation(table_name, "INSERT", key, existing)

        return True

    def update(self, txn, table_name, key, new_value):
        """
        Transactional update.
        Fails loudly if the key does not exist (unlike insert which upserts).
        """
        self._check_active(txn)
        self._acquire_lock(txn, table_name)

        table = self._get_table(table_name)

        old_value = table.data.search(key)
        if old_value is None:
            raise RuntimeError(
                f"Key {key} not found in '{table_name}' — cannot update."
            )

        # WAL first
        self.logger.log_write(
            txn.txn_id, table_name, "UPDATE", key, old_value, new_value
        )

        table.data.update(key, new_value)
        txn.record_operation(table_name, "UPDATE", key, old_value)

        return True

    def delete(self, txn, table_name, key):
        """
        Transactional delete.
        Saves the full record before removing it so rollback can restore it.
        """
        self._check_active(txn)
        self._acquire_lock(txn, table_name)

        table = self._get_table(table_name)

        old_value = table.data.search(key)
        if old_value is None:
            raise RuntimeError(
                f"Key {key} not found in '{table_name}' — cannot delete."
            )

        # WAL first
        self.logger.log_write(
            txn.txn_id, table_name, "DELETE", key, old_value, None
        )

        table.data.delete(key)
        txn.record_operation(table_name, "DELETE", key, old_value)

        return True

    def search(self, table_name, key, txn=None):
        """
        Point lookup.
        If a transaction is provided, acquires the table lock to prevent 
        concurrent modifications and avoid read-modify-write anomalies.
        """
        if txn:
            self._check_active(txn)
            self._acquire_lock(txn, table_name)
            
        table = self._get_table(table_name)
        return table.data.search(key)

    def range_query(self, table_name, start_key, end_key):
        """Read-only range query — no transaction or lock needed."""
        table = self._get_table(table_name)
        return table.data.range_query(start_key, end_key)

    # ------------------------------------------------------------------ #
    #  CRASH RECOVERY                                                      #
    # ------------------------------------------------------------------ #

    def _recover(self):
        """
        Called automatically at startup.

        ARIES-simplified algorithm:
          1. Read the full WAL log from disk
          2. Identify transactions that started (BEGIN) but never finished
             (no matching COMMIT or ROLLBACK)
          3. Undo their operations in reverse order
          4. Write a ROLLBACK record for each so the next restart sees them as clean

        This correctly handles a process killed mid-transaction.
        """
        entries = self.logger.read_log()
        if not entries:
            print("[Recovery] WAL is empty — clean start.")
            return

        txn_states = {}   # {txn_id: "INCOMPLETE" | "COMMITTED" | "ROLLED_BACK"}
        txn_ops    = {}   # {txn_id: [write entries in order]}

        for entry in entries:
            tid  = entry["txn_id"]
            etype = entry["type"]

            if etype == "BEGIN":
                txn_states[tid] = "INCOMPLETE"
                txn_ops[tid]    = []

            elif etype == "WRITE":
                if tid in txn_ops:
                    txn_ops[tid].append(entry)

            elif etype == "COMMIT":
                txn_states[tid] = "COMMITTED"

            elif etype == "ROLLBACK":
                txn_states[tid] = "ROLLED_BACK"

        incomplete = [
            tid for tid, state in txn_states.items()
            if state == "INCOMPLETE"
        ]

        if not incomplete:
            print("[Recovery] No incomplete transactions — clean state.")
            return

        print(f"[Recovery] {len(incomplete)} incomplete transaction(s) found: {incomplete}")
        print("[Recovery] Rolling back incomplete transactions...")

        for tid in incomplete:
            ops = txn_ops.get(tid, [])
            print(f"  [Recovery] Undoing TXN {tid} ({len(ops)} op(s))...")

            for op in reversed(ops):   # LIFO — last operation undone first
                undo_step = {
                    "table":     op["table"],
                    "operation": op["operation"],
                    "key":       op["key"],
                    "old_value": op["old_value"],
                }
                try:
                    self._apply_undo(undo_step)
                except Exception as e:
                    print(f"    [Recovery] Warning: could not undo op — {e}")

            # Mark this transaction as cleanly rolled back in the log
            self.logger.log_rollback(tid)
            print(f"  [Recovery] TXN {tid} rolled back successfully.")

        print("[Recovery] Recovery complete.")