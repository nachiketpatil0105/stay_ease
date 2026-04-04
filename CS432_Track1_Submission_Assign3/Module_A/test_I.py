# test_isolation.py
# Tests ISOLATION: Two threads try to run transactions concurrently.
# The lock ensures only one runs at a time — no corruption, no dirty reads.

import threading
import time
from setup_db import db_admin

results = {}

def transaction_thread_1():
    """Thread 1: Updates Room 101 capacity to 5, then restores it."""
    print("[Thread 1] Waiting to acquire lock...")
    db_admin.begin()

    try:
        rooms_table, _ = db_admin.get_table("stayease", "rooms")
        _, room = rooms_table.get(101)

        print(f"[Thread 1] Room 101 Capacity BEFORE: {room['Capacity']}")

        updated = room.copy()
        updated['Capacity'] = 5
        rooms_table.update(101, updated)

        print("[Thread 1] Set capacity to 5. Sleeping for 2 seconds...")
        time.sleep(2)  # Hold the lock — Thread 2 must wait

        # Restore original
        restored = room.copy()
        restored['Capacity'] = 2
        rooms_table.update(101, restored)

        db_admin.commit("stayease")
        print("[Thread 1] Committed. Lock released.")
        results['thread1'] = 'committed'

    except Exception as e:
        print(f"[Thread 1] Error: {e}")
        db_admin.rollback()
        results['thread1'] = 'rolled_back'


def transaction_thread_2():
    """Thread 2: Tries to update Member 112 status. Must wait for Thread 1."""
    time.sleep(0.3)  # Slight delay so Thread 1 starts first
    print("[Thread 2] Waiting to acquire lock...")
    db_admin.begin()

    try:
        members_table, _ = db_admin.get_table("stayease", "members")
        _, member = members_table.get(112)

        print(f"[Thread 2] Member 112 Status BEFORE: {member['Status']}")

        updated = member.copy()
        updated['Status'] = 'Inactive'
        members_table.update(112, updated)

        # Restore original
        restored = member.copy()
        restored['Status'] = 'Active'
        members_table.update(112, restored)

        db_admin.commit("stayease")
        print("[Thread 2] Committed.")
        results['thread2'] = 'committed'

    except Exception as e:
        print(f"[Thread 2] Error: {e}")
        db_admin.rollback()
        results['thread2'] = 'rolled_back'


def test_isolation():
    print("=" * 60)
    print("TEST: ISOLATION — Concurrent Transactions Serialized by Lock")
    print("=" * 60)

    t1 = threading.Thread(target=transaction_thread_1, name="Thread-1")
    t2 = threading.Thread(target=transaction_thread_2, name="Thread-2")

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    # --- Final state check ---
    rooms_table, _   = db_admin.get_table("stayease", "rooms")
    members_table, _ = db_admin.get_table("stayease", "members")

    _, room_final   = rooms_table.get(101)
    _, member_final = members_table.get(112)

    print(f"\n[FINAL] Room 101 Capacity   : {room_final['Capacity']}  (Expected: 2)")
    print(f"[FINAL] Member 112 Status   : {member_final['Status']}  (Expected: Active)")
    print(f"[FINAL] Thread 1 result     : {results.get('thread1')}")
    print(f"[FINAL] Thread 2 result     : {results.get('thread2')}")

    isolation_ok = (
        room_final['Capacity'] == 2 and
        member_final['Status'] == 'Active' and
        results.get('thread1') == 'committed' and
        results.get('thread2') == 'committed'
    )

    print("\n" + ("ISOLATION TEST PASSED" if isolation_ok else "ISOLATION TEST FAILED"))
    print("=" * 60)

test_isolation()