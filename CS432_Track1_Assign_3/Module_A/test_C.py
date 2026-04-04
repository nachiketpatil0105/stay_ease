# test_consistency.py
# Tests CONSISTENCY: After every transaction (commit or rollback),
# all relations must remain valid — no orphan records, no corrupt state.

from setup_db import db_admin

def test_consistency():
    print("=" * 60)
    print("TEST: CONSISTENCY — Relations Stay Valid After Operations")
    print("=" * 60)

    members_table, _ = db_admin.get_table("stayease", "members")
    rooms_table, _   = db_admin.get_table("stayease", "rooms")
    alloc_table, _   = db_admin.get_table("stayease", "room_allocations")

    # --- Scenario 1: Successful commit should keep data consistent ---
    print("\n[Scenario 1] Successful transaction — Insert new member + room + allocation")

    db_admin.begin()
    try:
        new_member = {
            'Member_ID': 130, 'First_Name': 'Test', 'Last_Name': 'User',
            'Gender': 'M', 'Age': 21, 'Contact_Number': '9000000001',
            'Email': 'testuser@student.com', 'Status': 'Active',
            'Role_ID': 1, 'Image_Path': 'uploads/default.png',
            'Emergency_Contact': '9000000002'
        }
        members_table.insert(new_member)

        new_room = {
            'Room_ID': 303, 'Room_Number': '303', 'Hostel_ID': 2,
            'Floor_Number': 3, 'Capacity': 2
        }
        rooms_table.insert(new_room)

        new_alloc = {
            'Allocation_ID': 20, 'Member_ID': 130, 'Room_ID': 303,
            'Allocation_Date': '2026-04-01', 'Check_Out_Date': 'None',
            'Status': 'Active'
        }
        alloc_table.insert(new_alloc)

        db_admin.commit("stayease")
        print("[Step] Transaction committed successfully.")

    except Exception as e:
        print(f"[ERROR] {e}")
        db_admin.rollback()

    # --- Verify all three records exist ---
    member_exists, _ = members_table.get(130)
    room_exists, _   = rooms_table.get(303)
    alloc_exists, alloc_data  = alloc_table.get(20)

    print(f"\n[CHECK] Member 130 exists  : {member_exists}  (Expected: True)")
    print(f"[CHECK] Room 303 exists    : {room_exists}   (Expected: True)")
    print(f"[CHECK] Allocation 20 exists: {alloc_exists}  (Expected: True)")

    # --- Referential Integrity Check ---
    ref_member_ok, ref_room_ok = False, False
    if alloc_exists:
        ref_member_ok, _ = members_table.get(alloc_data['Member_ID'])
        ref_room_ok, _   = rooms_table.get(alloc_data['Room_ID'])
    print(f"[CHECK] Allocation 20 Member_ID refs valid member : {ref_member_ok}  (Expected: True)")
    print(f"[CHECK] Allocation 20 Room_ID refs valid room     : {ref_room_ok}   (Expected: True)")

    # --- Scenario 2: After rollback, no partial data ---
    print("\n[Scenario 2] Failed transaction — Partial inserts must not persist")

    db_admin.begin()
    try:
        partial_member = {
            'Member_ID': 131, 'First_Name': 'Ghost', 'Last_Name': 'User',
            'Gender': 'M', 'Age': 22, 'Contact_Number': '9000000003',
            'Email': 'ghost@student.com', 'Status': 'Active',
            'Role_ID': 1, 'Image_Path': 'uploads/default.png',
            'Emergency_Contact': '9000000004'
        }
        members_table.insert(partial_member)
        print("[Step] Inserted Member 131 (partial).")

        # Deliberate failure before room/allocation insert
        raise RuntimeError("Simulated crash before completing transaction.")

        db_admin.commit("stayease")

    except Exception as e:
        print(f"[ERROR] Caught: {e}")
        db_admin.rollback()

    ghost_exists, _ = members_table.get(131)
    print(f"\n[CHECK] Ghost Member 131 exists: {ghost_exists}  (Expected: False)")

    # --- Pass / Fail ---
    consistency_ok = (
        member_exists and room_exists and alloc_exists and
        ref_member_ok and ref_room_ok and
        not ghost_exists
    )

    print("\n" + ("CONSISTENCY TEST PASSED" if consistency_ok else "CONSISTENCY TEST FAILED"))
    print("=" * 60)

    # --- Cleanup: remove test data ---
    db_admin.begin()
    alloc_table.delete(20)
    rooms_table.delete(303)
    members_table.delete(130)
    db_admin.commit("stayease")
    print("[Cleanup] Test records removed.")

test_consistency()