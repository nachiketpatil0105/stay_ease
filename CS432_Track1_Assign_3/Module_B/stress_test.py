import threading
import time
import random
import os
from setup_db import db_admin

current_folder = os.path.dirname(os.path.abspath(__file__))

db_admin.log_file = os.path.join(current_folder, "stress_wal.log")


# Track our results across the 100 threads
results = {
    "success": 0,
    "room_full_rejections": 0,
    "simulated_crashes": 0,
    "unexpected_errors": 0
}

def book_room(user_id):
    """
    A single user trying to book a bed in Room 101.
    """
    time.sleep(random.uniform(0.1, 0.5)) 
    
    db_admin.begin()
    try:
        # Grab ALL THREE tables
        members_table, _ = db_admin.get_table("stayease", "members")
        rooms_table, _ = db_admin.get_table("stayease", "rooms")
        alloc_table, _ = db_admin.get_table("stayease", "room_allocations")
        
        _, room = rooms_table.get(101)


        # SIMULATE FAILURE UNDER STRESS
        if user_id % 20 == 0:
            raise RuntimeError("Simulated network failure mid-transaction!")
        
        # 1. Check Capacity
        if room['Capacity'] <= 0:
            db_admin.rollback()
            results["room_full_rejections"] += 1
            return
            
        # 2. TABLE 1: Insert the New Member
        new_member = {
            'Member_ID': user_id + 5000, # +5000 so we don't overwrite Ravi (112)
            'First_Name': f'StressTest_{user_id}', 
            'Last_Name': 'User',
            'Gender': 'M', 
            'Age': 20, 
            'Contact_Number': '0000000000',
            'Email': f'user{user_id}@test.com', 
            'Emergency_Contact': '0000000000', 
            'Image_Path': 'uploads/default.jpg',
            'Role_ID': 1, 
            'Status': 'Active'
        }
        members_table.insert(new_member)

        # 3. TABLE 2: Update Room Capacity
        updated_room = room.copy()
        updated_room['Capacity'] -= 1
        rooms_table.update(101, updated_room)
        
        # 4. TABLE 3: Insert Allocation
        new_alloc = {
            'Allocation_ID': user_id + 8000, 
            'Member_ID': user_id + 5000, 
            'Room_ID': 101,
            'Allocation_Date': '2026-04-05', 
            'Check_Out_Date': 'None',
            'Status': 'Active'
        }
        alloc_table.insert(new_alloc)
        
        
            
        db_admin.commit("stayease")
        results["success"] += 1
        
    except RuntimeError:
        db_admin.rollback()
        results["simulated_crashes"] += 1
    except Exception as e:
        db_admin.rollback()
        results["unexpected_errors"] += 1


def run_stress_test():
    print("=" * 60)
    print("MODULE B: STRESS TEST & RACE CONDITION DEFENSE")
    print("=" * 60)
    
    # SETUP: Set Room 101 to have exactly 5 beds
    db_admin.begin()
    rooms_table, _ = db_admin.get_table("stayease", "rooms")
    _, room = rooms_table.get(101)
    updated_room = room.copy()
    updated_room['Capacity'] = 5
    rooms_table.update(101, updated_room)
    db_admin.commit("stayease")
    
    print("\n[START] Room 101 capacity set to 5.")
    print("[START] Unleashing 100 concurrent booking requests...")
    
    start_time = time.time()
    
    # Create and start 100 threads
    threads = []
    for i in range(1, 101):
        t = threading.Thread(target=book_room, args=(i,))
        threads.append(t)
        t.start()
        
    # Wait for all 100 threads to finish
    for t in threads:
        t.join()
        
    end_time = time.time()
    
    # VERIFICATION
    db_admin.begin()
    _, final_room = rooms_table.get(101)
    db_admin.rollback() # Just reading, no need to commit
    
    print("\n" + "=" * 60)
    print("STRESS TEST RESULTS")
    print("=" * 60)
    print(f"Total Execution Time  : {end_time - start_time:.2f} seconds")
    print(f"Successful Bookings   : {results['success']} (Expected: 5)")
    print(f"Room Full Rejections  : {results['room_full_rejections']} (Expected: 90)")
    print(f"Simulated Crashes     : {results['simulated_crashes']} (Expected: 5)")
    print(f"Unexpected Errors     : {results['unexpected_errors']} (Expected: 0)")
    print(f"\n[FINAL] Room 101 Capacity Remaining: {final_room['Capacity']} (Expected: 0)")
    
    if final_room['Capacity'] == 0 and results['success'] == 5:
        print("\nMODULE B CONCURRENCY TEST PASSED PERFECTLY!")
    else:
        print("\nRACE CONDITION DETECTED! Database corrupted.")

if __name__ == "__main__":
    run_stress_test()