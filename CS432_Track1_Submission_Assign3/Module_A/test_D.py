# test_durability.py
# Tests DURABILITY: Once committed, data must survive a system restart.
# Simulates restart by creating a fresh DatabaseManager and reloading from disk.

from db_manager import DatabaseManager

def simulate_first_run():
    """First run: insert data across 3 tables and commit."""
    print("=" * 60)
    print("TEST: DURABILITY — Committed Data Survives Restart")
    print("=" * 60)

    print("\n[Phase 1] First Run — Committing data to disk...")

    # Fresh DB instance (simulates first boot)
    db = DatabaseManager()
    db.create_database("stayease")

    members_schema = {
        'Member_ID': int, 'First_Name': str, 'Last_Name': str,
        'Gender': str, 'Age': int, 'Contact_Number': str,
        'Email': str, 'Emergency_Contact': str, 'Image_Path': str,
        'Role_ID': int, 'Status': str
    }
    rooms_schema = {
        'Room_ID': int, 'Room_Number': str, 'Hostel_ID': int,
        'Floor_Number': int, 'Capacity': int
    }
    allocations_schema = {
        'Allocation_ID': int, 'Member_ID': int, 'Room_ID': int,
        'Allocation_Date': str, 'Check_Out_Date': str, 'Status': str
    }

    db.create_table("stayease", "members", members_schema, search_key="Member_ID")
    db.create_table("stayease", "rooms", rooms_schema, search_key="Room_ID")
    db.create_table("stayease", "room_allocations", allocations_schema, search_key="Allocation_ID")

    members_table, _ = db.get_table("stayease", "members")
    rooms_table, _   = db.get_table("stayease", "rooms")
    alloc_table, _   = db.get_table("stayease", "room_allocations")

    # Begin transaction across all 3 tables
    db.begin()

    member_data = {
        'Member_ID': 200, 'First_Name': 'Durability', 'Last_Name': 'Test',
        'Gender': 'M', 'Age': 25, 'Contact_Number': '9111111111',
        'Email': 'durability@test.com', 'Status': 'Active',
        'Role_ID': 1, 'Image_Path': 'uploads/default.png',
        'Emergency_Contact': '9111111112'
    }
    room_data = {
        'Room_ID': 400, 'Room_Number': '400', 'Hostel_ID': 2,
        'Floor_Number': 4, 'Capacity': 2
    }
    alloc_data = {
        'Allocation_ID': 50, 'Member_ID': 200, 'Room_ID': 400,
        'Allocation_Date': '2026-04-03', 'Check_Out_Date': 'None',
        'Status': 'Active'
    }

    members_table.insert(member_data)
    rooms_table.insert(room_data)
    alloc_table.insert(alloc_data)

    db.commit("stayease")
    print("[Phase 1] Committed Member 200, Room 400, Allocation 50.")
    print("[Phase 1] Data saved to .tree files. Simulating restart...\n")

    # DB object goes out of scope here — simulates shutdown
    del db


def simulate_restart():
    """Second run: fresh instance, reload from disk, verify data is there."""
    print("[Phase 2] Restart — Loading from disk...")

    # Fresh DB instance (simulates reboot)
    db = DatabaseManager()
    db.create_database("stayease")

    members_schema = {
        'Member_ID': int, 'First_Name': str, 'Last_Name': str,
        'Gender': str, 'Age': int, 'Contact_Number': str,
        'Email': str, 'Emergency_Contact': str, 'Image_Path': str,
        'Role_ID': int, 'Status': str
    }
    rooms_schema = {
        'Room_ID': int, 'Room_Number': str, 'Hostel_ID': int,
        'Floor_Number': int, 'Capacity': int
    }
    allocations_schema = {
        'Allocation_ID': int, 'Member_ID': int, 'Room_ID': int,
        'Allocation_Date': str, 'Check_Out_Date': str, 'Status': str
    }

    db.create_table("stayease", "members", members_schema, search_key="Member_ID")
    db.create_table("stayease", "rooms", rooms_schema, search_key="Room_ID")
    db.create_table("stayease", "room_allocations", allocations_schema, search_key="Allocation_ID")

    # Reload from disk — this is what survive restart means
    db.reload_all("stayease")
    db.recover("stayease")

    members_table, _ = db.get_table("stayease", "members")
    rooms_table, _   = db.get_table("stayease", "rooms")
    alloc_table, _   = db.get_table("stayease", "room_allocations")

    member_found, member_data = members_table.get(200)
    room_found, room_data     = rooms_table.get(400)
    alloc_found, alloc_data   = alloc_table.get(50)

    print(f"\n[CHECK] Member 200 found    : {member_found}  (Expected: True)")
    if member_found:
        print(f"        Name               : {member_data['First_Name']} {member_data['Last_Name']}")

    print(f"[CHECK] Room 400 found      : {room_found}   (Expected: True)")
    if room_found:
        print(f"        Floor              : {room_data['Floor_Number']}")

    print(f"[CHECK] Allocation 50 found : {alloc_found}  (Expected: True)")
    if alloc_found:
        print(f"        Status             : {alloc_data['Status']}")

    durability_ok = member_found and room_found and alloc_found

    print("\n" + ("✅ DURABILITY TEST PASSED" if durability_ok else "❌ DURABILITY TEST FAILED"))
    print("=" * 60)

    # --- Cleanup ---
    db.begin()
    alloc_table.delete(50)
    rooms_table.delete(400)
    members_table.delete(200)
    db.commit("stayease")
    print("[Cleanup] Test records removed.")


simulate_first_run()
simulate_restart()