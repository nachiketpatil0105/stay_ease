import threading
import requests

# The URL to your Flask app
BASE_URL = "http://127.0.0.1:5001"
NUM_STUDENTS = 5

# Create a barrier that waits for exactly 5 threads
sync_barrier = threading.Barrier(NUM_STUDENTS)

def student_submit_complaint(email, subcategory_id, description):
    """Simulates a student logging in, waiting at the barrier, and firing simultaneously."""
    session = requests.Session()
    
    # 1. SETUP PHASE: Log in as the specific student
    login_data = {"email": email, "password": "password123"}
    session.post(f"{BASE_URL}/", data=login_data)
    
    payload = {
        "subcategory": subcategory_id,
        "description": description
    }
    
    print(f"[{email}] Logged in and waiting at the starting gate...")
    
    # 2. THE BARRIER: The thread pauses here until all 5 threads arrive
    sync_barrier.wait() 
    
    # 3. THE SPRINT: All threads execute this line simultaneously!
    response = session.post(f"{BASE_URL}/submit_complaint", data=payload)
    
    if response.status_code == 200:
        print(f"[{email}] ✅ Ticket successfully sent to server!")
    else:
        print(f"[{email}] ❌ FAILED with status code: {response.status_code}")

if __name__ == "__main__":
    print("--- STARTING SYNCHRONIZED CONCURRENT USAGE TEST ---")
    
    students = [
        ("student1@stayease.com", 2, "Room 201 - Power completely out!"),
        ("student2@stayease.com", 2, "Room 201 - My laptop charger just sparked!"),
        ("student3@stayease.com", 2, "Room 202 - Lights are flickering heavily."),
        ("student4@stayease.com", 2, "Room 301 - Fan stopped working."),
        ("student5@stayease.com", 2, "Room 101 - Total blackout in my room.")
    ]
    
    threads = []
    for email, sub_id, desc in students:
        t = threading.Thread(target=student_submit_complaint, args=(email, sub_id, desc))
        threads.append(t)
        t.start()
    
    # Wait for all students to finish
    for t in threads:
        t.join()
    
    print("--- TEST COMPLETE ---")
    print("Log in to the Admin Dashboard to verify the complaints!")