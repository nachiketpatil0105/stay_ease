import os
from db_engine.db_manager import DatabaseManager
from db_engine.transaction_manager import TransactionManager

def print_database_state(members, rooms, allocations):
    print("\nCURRENT DATABASE STATE")
    print("Members:    ", members.get_all())
    print("Rooms:      ", rooms.get_all())
    print("Allocations:", allocations.get_all())
    

def main():
    # Initialize the Database and Transaction Manager
    print("Initializing StayEase Custom B+ Tree Database")
    db = DatabaseManager()
    db.create_database("stayease")
    
    # Create the 3 required tables
    db.create_table("stayease", "members", {"Member_ID": int, "Name": str, "Fee_Balance": float}, search_key="Member_ID")
    db.create_table("stayease", "rooms", {"Room_Number": str, "Available_Beds": int}, search_key="Room_Number")
    db.create_table("stayease", "allocations", {"Alloc_ID": int, "Member_ID": int, "Room_Number": str}, search_key="Alloc_ID")
    
    tx_manager = TransactionManager(db, log_file="stayease_wal.log")
    
    # Grab references to the tables
    # Grab references to the tables (Index 0 is the Table object)
    members = db.get_table("stayease", "members")[0]
    rooms = db.get_table("stayease", "rooms")[0]
    allocations = db.get_table("stayease", "allocations")[0]
    
    # Insert Initial Mock Data
    members.insert({"Member_ID": 110, "Name": "Priya", "Fee_Balance": 0.0})
    members.insert({"Member_ID": 111, "Name": "Rahul", "Fee_Balance": 0.0})
    rooms.insert({"Room_Number": "101", "Available_Beds": 2})
    
    print_database_state(members, rooms, allocations)

    
    # SCENARIO 1: A SUCCESSFUL TRANSACTION
    print(">>> SCENARIO 1: Priya successfully books Room 101.")
    tid1 = tx_manager.begin_transaction()
    try:
        # Action 1: Decrease Available Beds
        room101 = rooms.get("101")[1]
        room101["Available_Beds"] -= 1
        rooms.update("101", room101, tx_manager, tid1)
        
        # Action 2: Increase Fee Balance
        priya = members.get(110)[1]
        priya["Fee_Balance"] += 25000.0
        members.update(110, priya, tx_manager, tid1)
        
        # Action 3: Insert Allocation Record
        allocations.insert({"Alloc_ID": 1, "Member_ID": 110, "Room_Number": "101"}, tx_manager, tid1)
        
        tx_manager.commit(tid1)
        print(f" {tid1} COMMITTED SUCCESSFULLY.")
    except Exception as e:
        tx_manager.rollback(tid1)

    print_database_state(members, rooms, allocations)

    
    # SCENARIO 2: A FAILED TRANSACTION (CRASH SIMULATION)
    print(">>> SCENARIO 2: Rahul tries to book Room 101, but the system CRASHES halfway through!")
    tid2 = tx_manager.begin_transaction()
    try:
        # Action 1: Decrease Available Beds
        room101 = rooms.get("101")[1]
        room101["Available_Beds"] -= 1
        rooms.update("101", room101, tx_manager, tid2)
        
        # Action 2: Increase Fee Balance
        rahul = members.get(111)[1]
        rahul["Fee_Balance"] += 25000.0
        members.update(111, rahul, tx_manager, tid2)
        
        #  CRASH THE SYSTEM BEFORE INSERTING THE ALLOCATION 
        print(" CRITICAL ERROR: POWER OUTAGE SIMULATED! ")
        raise Exception("System crashed before allocation could be saved!")
        
        # This code will never run because of the crash above
        allocations.insert({"Alloc_ID": 2, "Member_ID": 111, "Room_Number": "101"}, tx_manager, tid2)
        tx_manager.commit(tid2)
        
    except Exception as e:
        print(f" Error caught: {e}")
        # The Transaction Manager catches the crash and UNDOES Action 1 and Action 2
        tx_manager.rollback(tid2)

    print_database_state(members, rooms, allocations)

if __name__ == "__main__":
    # Clean up old log file if it exists for a fresh test
    if os.path.exists("stayease_wal.log"):
        os.remove("stayease_wal.log")
    main()