import os
import json
from datetime import datetime
from db_engine.db_manager import DatabaseManager
from db_engine.transaction_manager import TransactionManager

def main():
    print("STARTING MODULE A: DURABILITY & RECOVERY TEST")
    
    # Setup DB
    db = DatabaseManager()
    db.create_database("stayease")
    db.create_table("stayease", "rooms", {"Room_Number": str, "Available_Beds": int}, search_key="Room_Number")
    rooms = db.get_table("stayease", "rooms")[0]
    
    # Insert initial data
    rooms.insert({"Room_Number": "101", "Available_Beds": 2})
    print("Initial State: Room 101 has 2 beds.")
    
    # Simulate a dirty log file (Server crashed halfway through a booking)
    print("\nSimulating a sudden power loss, writing an incomplete transaction to the WAL")
    with open("stayease_wal.log", "w") as f:
        # Write a BEGIN but no COMMIT
        f.write(json.dumps({"timestamp": str(datetime.now()), "tid": "TXN-CRASH-999", "action": "BEGIN", "data": {}}) + "\n")
        f.write(json.dumps({
            "timestamp": str(datetime.now()), 
            "tid": "TXN-CRASH-999", 
            "action": "UPDATE", 
            "data": {
                "table": "rooms", 
                "action": "UPDATE", 
                "key": "101", 
                "old_record": {"Room_Number": "101", "Available_Beds": 2}, 
                "new_record": {"Room_Number": "101", "Available_Beds": 1}
            }
        }) + "\n")
    
    # Manually apply the "dirty" state to the B+ Tree to simulate where it was at the moment of the crash
    rooms.update("101", {"Room_Number": "101", "Available_Beds": 1})
    print("Crash State: Room 101 has 1 bed, but no COMMIT was ever recorded.")
    
    # Boot up the Transaction Manager (Server Restarts)
    print("\nServer Rebooting... Initializing Transaction Manager...")
    tx_manager = TransactionManager(db, log_file="stayease_wal.log")
    
    # Run Recovery
    tx_manager.recover()
    
    # Verify
    final_beds = rooms.get("101")[1]["Available_Beds"]
    print(f"\nFinal State after Recovery: Room 101 has {final_beds} beds.")
    if final_beds == 2:
        print("DURABILITY TEST PASSED: Incomplete transactions were successfully undone on restart!")
    else:
        print("DURABILITY TEST FAILED.")

if __name__ == "__main__":
    main()