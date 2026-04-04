import os
from db_manager import DatabaseManager
from transaction_manager import TransactionManager

def simulate_system_crash():
    print("--- STARTING FAILURE SIMULATION ---")
    
    # 1. Connect to the StayEase Database
    db = DatabaseManager()
    if not db.load_from_disk("db_snapshot.pkl"):
        print("Error: Database not found. Run hard_reset.py first.")
        return
        
    tm = TransactionManager(db, "stayease", log_file="stayease_wal.log")
    
    # Data for our test
    test_student_id = 999
    test_room_id = 201
    
    # Verify the student does NOT exist before we start
    member_table, _ = db.get_table("stayease", "members")
    if member_table.data.search(test_student_id):
        print("Please run hard_reset.py first. Test student already exists.")
        return

    print("\n[Step 1] Admin initiates Bulk Enrollment...")
    txn = tm.begin_transaction()
    
    try:
        # Action A: Insert the new student into the database
        print(f"[Step 2] Inserting Student ID {test_student_id} (Rahul Sharma) into Members table...")
        tm.insert(txn, "members", test_student_id, {
            "Member_ID": test_student_id, "First_Name": "Rahul", "Last_Name": "Sharma",
            "Gender": "M", "Age": 19, "Contact_Number": "9999900000",
            "Email": "rahul.test@stayease.com", "Password": "password123", 
            "Emergency_Contact": "0000000000", "Image_Path": "default.png", 
            "Role_ID": 1, "Status": "Active"
        })
        
        # Verify the student is TEMPORARILY in the database
        temp_check = member_table.data.search(test_student_id)
        print(f"         -> Verification: Student {temp_check['First_Name']} is currently in RAM.")
        
        # Action B: SIMULATE A MASSIVE SYSTEM CRASH!
        print("[Step 3] Attempting to allocate room... 💥 FATAL ERROR: SERVER POWER LOSS 💥")
        raise RuntimeError("CRITICAL SYSTEM FAILURE: Database connection lost mid-transaction!")
        
        # This line will NEVER be reached because of the crash
        tm.insert(txn, "room_allocations", 9999, {
            "Allocation_ID": 9999, "Member_ID": test_student_id, "Room_ID": test_room_id,
            "Allocation_Date": "2026-04-04", "Check_Out_Date": "None", "Status": "Active"
        })
        
        tm.commit(txn)
        
    except Exception as e:
        print(f"\n[SYSTEM ALERT] Caught Exception: {e}")
        print("[SYSTEM ALERT] Initiating Emergency Rollback Protocol...")
        # The TransactionManager undoes every step in the undo_log
        tm.rollback(txn)
        
    print("\n--- VERIFYING DATABASE INTEGRITY ---")
    # Search the database again for the student
    final_check = member_table.data.search(test_student_id)
    
    if final_check is None:
        print(f"✅ SUCCESS: Student ID {test_student_id} was successfully wiped from the database.")
        print("✅ SUCCESS: No partial data exists. The database is 100% consistent.")
    else:
        print(f"❌ FAILURE: Ghost data found! Student {final_check['First_Name']} is stuck in the database!")

if __name__ == "__main__":
    simulate_system_crash()