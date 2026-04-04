# stress_test.py
import threading
import time
import concurrent.futures
from db_engine.db_manager import DatabaseManager
from db_engine.transaction_manager import TransactionManager

# Global counters for report
success_count = 0
fail_count = 0
counter_lock = threading.Lock()

def book_room(student_id, db, tx_manager):
    global success_count, fail_count
    tid = tx_manager.begin_transaction()
    
    try:
        rooms = db.get_table("stayease", "rooms")[0]
        allocations = db.get_table("stayease", "allocations")[0]
        
        # Read current capacity
        room101 = rooms.get("101")[1]
        
        # Simulate slight processing delay to force race conditions
        time.sleep(0.01) 
        
        if room101["Available_Beds"] > 0:
            # Book it
            room101["Available_Beds"] -= 1
            rooms.update("101", room101, tx_manager, tid)
            
            allocations.insert({
                "Alloc_ID": student_id, 
                "Member_ID": student_id, 
                "Room_Number": "101"
            }, tx_manager, tid)
            
            tx_manager.commit(tid)
            with counter_lock:
                success_count += 1
        else:
            raise ValueError("Room is fully booked!")
            
    except Exception as e:
        tx_manager.rollback(tid)
        with counter_lock:
            fail_count += 1

def main():
    print("STARTING MODULE B: STRESS TEST")
    db = DatabaseManager()
    db.create_database("stayease")
    db.create_table("stayease", "rooms", {"Room_Number": str, "Available_Beds": int}, search_key="Room_Number")
    db.create_table("stayease", "allocations", {"Alloc_ID": int, "Member_ID": int, "Room_Number": str}, search_key="Alloc_ID")
    
    tx_manager = TransactionManager(db, log_file="stress_wal.log")
    
    # Initialize Room 101 with exactly 2 beds
    rooms = db.get_table("stayease", "rooms")[0]
    rooms.insert({"Room_Number": "101", "Available_Beds": 2})
    
    print("Room 101 initialized with 2 beds.")
    print("Firing 100 concurrent booking requests...\n")
    
    # Fire 100 threads simultaneously!
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(book_room, i, db, tx_manager) for i in range(1, 101)]
        concurrent.futures.wait(futures)
        
    end_time = time.time()
    
    print("STRESS TEST COMPLETE")
    print(f"Total Time: {end_time - start_time:.4f} seconds")
    print(f"Successful Bookings: {success_count} (Expected: 2)")
    print(f"Failed/Rejected Bookings: {fail_count} (Expected: 98)")
    
    final_beds = rooms.get("101")[1]["Available_Beds"]
    print(f"Final Available Beds in Room 101: {final_beds} (Expected: 0)")
    
    if success_count == 2 and final_beds == 0:
        print("\nISOLATION TEST PASSED: No race conditions or double-bookings occurred!")
    else:
        print("\nISOLATION TEST FAILED: Race condition detected.")

if __name__ == "__main__":
    main()