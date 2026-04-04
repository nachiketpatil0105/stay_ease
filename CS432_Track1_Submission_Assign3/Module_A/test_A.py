# test_atomicity.py
# Tests ATOMICITY: If any step in a multi-table transaction fails,
# ALL changes must be rolled back. No partial updates should remain.

from setup_db import db_admin

def test_atomicity():
    print("=" * 60)
    print("TEST: ATOMICITY — Multi-Table Rollback on Failure")
    print("=" * 60)

    members_table, _  = db_admin.get_table("stayease", "members")
    rooms_table, _    = db_admin.get_table("stayease", "rooms")
    alloc_table, _    = db_admin.get_table("stayease", "room_allocations")

    # --- Record state BEFORE transaction ---
    _, member_before  = members_table.get(112)
    _, room_before    = rooms_table.get(101)
    alloc_before_all  = alloc_table.get_all()
    alloc_ids_before  = [k for k, v in alloc_before_all]

    print(f"\n[BEFORE] Member 112 Status  : {member_before['Status']}")
    print(f"[BEFORE] Room 101 Capacity  : {room_before['Capacity']}")
    print(f"[BEFORE] Allocation IDs     : {alloc_ids_before}")

    # --- Begin Transaction ---
    db_admin.begin()

    try:
        # Step 1: Update Member 112 status (Table 1)
        updated_member = member_before.copy()
        updated_member['Status'] = 'Inactive'
        members_table.update(112, updated_member)
        print("\n[Step 1] Member 112 status set to Inactive.")

        # Step 2: Update Room 101 capacity (Table 2)
        updated_room = room_before.copy()
        updated_room['Capacity'] = 99
        rooms_table.update(101, updated_room)
        print("[Step 2] Room 101 capacity set to 99.")

        # Step 3: Insert an INVALID allocation to trigger failure (Table 3)
        print("[Step 3] Attempting to insert invalid allocation...")
        invalid_alloc = {'Allocation_ID': 999}  # Missing required fields
        success, msg = alloc_table.insert(invalid_alloc)
        if not success:
            raise ValueError(f"Simulated Failure: {msg}")

        db_admin.commit("stayease")
        print("COMMIT — should NOT reach here.")

    except Exception as e:
        print(f"\n[ERROR] Caught: {e}")
        db_admin.rollback()

    # --- Verify state AFTER rollback ---
    print("\n--- VERIFICATION ---")

    _, member_after = members_table.get(112)
    _, room_after   = rooms_table.get(101)
    alloc_after_all = alloc_table.get_all()
    alloc_ids_after = [k for k, v in alloc_after_all]

    print(f"[AFTER] Member 112 Status   : {member_after['Status']}  (Expected: Active)")
    print(f"[AFTER] Room 101 Capacity   : {room_after['Capacity']}  (Expected: 2)")
    print(f"[AFTER] Allocation IDs      : {alloc_ids_after}  (Expected: [1, 2] — no 999)")

    # --- Pass / Fail ---
    atomicity_ok = (
        member_after['Status'] == 'Active' and
        room_after['Capacity'] == 2 and
        999 not in alloc_ids_after
    )

    print("\n" + ("ATOMICITY TEST PASSED" if atomicity_ok else "ATOMICITY TEST FAILED"))
    print("=" * 60)

test_atomicity()