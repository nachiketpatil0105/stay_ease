# Module A — Transaction Management, Concurrency Control & ACID Validation

## CS 432 – Databases | Assignment 3 | IIT Gandhinagar
**Project:** StayEase — Hostel Management System  
**Instructor:** Dr. Yogesh K. Meena | Semester II (2025–2026)

---

## Overview

This module extends the B+ Tree based database engine from Assignment 2 to support full transaction management, crash recovery, and ACID compliance across three relations — **Members**, **Rooms**, and **Room Allocations** — each stored in a dedicated B+ Tree.

---

## Folder Structure

```
Module_A/
├── transaction_manager.py   # Superclass — BEGIN, COMMIT, ROLLBACK, WAL, RECOVERY
├── db_manager.py            # Inherits TransactionManager — manages databases and tables
├── table.py                 # Table abstraction over B+ Tree — logs every operation
├── bplustree.py             # Core B+ Tree storage engine
├── setup_db.py              # Initializes DB, loads from disk, inserts seed data
├── test_A.py                # Atomicity test
├── test_C.py                # Consistency test
├── test_I.py                # Isolation test
├── test_D.py                # Durability test
├── demo.ipynb               # Full ACID demonstration notebook
├── stayease_wal.log         # Write-Ahead Log file
├── data/                    # Pickle files for B+ Tree persistence
│   ├── members.tree
│   ├── rooms.tree
│   └── room_allocations.tree
└── uploads/
    └── default.jpg
```

---

## How to Run

### Step 1 — Clean previous state (first time or fresh run)
```bash
rm -rf data/ stayease_wal.log
```

### Step 2 — Initialize the database
```bash
python3 setup_db.py
```

### Step 3 — Run ACID tests in order
```bash
python3 test_A.py   # Atomicity
python3 test_C.py   # Consistency
python3 test_I.py   # Isolation
python3 test_D.py   # Durability
```

### Step 4 — Or run everything in the notebook
```bash
jupyter notebook demo.ipynb
```
Run all cells from top to bottom.

---

## Architecture

### TransactionManager (`transaction_manager.py`)
Superclass of `DatabaseManager`. Handles all transaction logic.

| Component | Purpose |
|---|---|
| `threading.Lock` | Ensures only one transaction runs at a time |
| `active_transaction` | In-memory journal of all ops for rollback |
| `stayease_wal.log` | Write-Ahead Log with tx_id and timestamp |
| `_current_tx_id` | Unique UUID per transaction for traceability |

| Method | Description |
|---|---|
| `begin()` | Acquires lock, generates tx_id, writes BEGIN to WAL |
| `commit()` | Writes COMMIT to WAL, persists all B+ Trees to disk, releases lock |
| `rollback()` | Undoes all journal ops in reverse (LIFO), removes incomplete tx from WAL, releases lock |
| `recover()` | Reads WAL, REDOs committed transactions, UNDOs incomplete ones |
| `_write_to_log()` | Appends operation with tx_id and timestamp to WAL |

### DatabaseManager (`db_manager.py`)
Inherits from `TransactionManager`. Manages databases, tables, and disk persistence.

### Table (`table.py`)
Wraps a B+ Tree. Every `insert()`, `update()`, `delete()` logs to both the in-memory journal and the WAL before modifying the tree.

### BPlusTree (`bplustree.py`)
Primary storage engine. One tree per table. Primary key is the tree key. Full record is the value.

---

## ACID Properties

### Atomicity — `test_A.py`
A transaction updates Member 112 and Room 101, then attempts an invalid allocation insert. The insert fails, triggering rollback. All changes are undone. Incomplete entry is removed from WAL.

**Expected:** Member 112 Status = Active, Room 101 Capacity = 2, no record 999

### Consistency — `test_C.py`
**Scenario 1:** Inserts Member 130, Room 303, Allocation 20 in one transaction. After commit, referential integrity is verified — allocation references valid member and room.  
**Scenario 2:** Inserts Ghost Member 131 then crashes. Rollback removes the ghost. No orphan records remain.

**Expected:** All references valid, Ghost Member 131 absent after rollback

### Isolation — `test_I.py`
Two threads run concurrently. Thread 1 holds the lock for 2 seconds. Thread 2 blocks until Thread 1 commits. No interleaving, no dirty reads.

**Expected:** Both threads commit, final state unchanged, WAL shows two separate tx_ids

### Durability — `test_D.py`
Phase 1 commits Member 200, Room 400, Allocation 50 to disk and destroys the object. Phase 2 creates a fresh instance, reloads from disk, calls recover(). All three records are found.

**Expected:** All records survive object destruction and fresh instance reload

---

## WAL Log Format

Every entry in `stayease_wal.log` is a JSON line:

```json
{"tx_id": "a1b2c3d4", "timestamp": "2026-04-05 14:32:01", "op": "BEGIN", "table": null, "key": null, "data": null}
{"tx_id": "a1b2c3d4", "timestamp": "2026-04-05 14:32:01", "op": "INSERT", "table": "members", "key": 130, "data": {...}}
{"tx_id": "a1b2c3d4", "timestamp": "2026-04-05 14:32:02", "op": "UPDATE", "table": "rooms", "key": 101, "data": {"old": {...}, "new": {...}}}
{"tx_id": "a1b2c3d4", "timestamp": "2026-04-05 14:32:02", "op": "COMMIT", "table": null, "key": null, "data": null}
```

- **INSERT** — stores full new record
- **UPDATE** — stores both old and new record for UNDO and REDO
- **DELETE** — stores old record for UNDO
- **Incomplete transactions** are removed from log after rollback or recovery
- **Committed transactions** are always retained in log

---

## Seed Data

Inserted automatically by `setup_db.py` if not already present:

| Table | Records |
|---|---|
| Members | Member 110 — Priya Sharma, Member 112 — Ravi Kumar |
| Rooms | Room 101 — Floor 1, Capacity 2 |
| Room Allocations | Allocation 1 (Priya → Room 101), Allocation 2 (Ravi → Room 101) |

---

## Dependencies

```bash
pip3 install jupyter
```

No other external dependencies. All storage is custom B+ Tree based.

