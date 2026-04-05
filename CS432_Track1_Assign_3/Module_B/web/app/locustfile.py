from locust import HttpUser, task, between
import random

class StayEaseStressTest(HttpUser):
    # Wait between 1 to 2 seconds between clicks
    wait_time = between(1, 2)

    # PASTE YOUR COPIED BROWSER TOKEN HERE
    # (Keep it inside the quotation marks!)
    admin_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwibWVtYmVyX2lkIjoxMDAsInJvbGUiOiJBZG1pbiIsImV4cCI6MTc3NTM0NTA0M30.FmzNzN4veJrecNlcZFVORnRXyGaVF_gwTquAootu81U" 

    @task
    def book_room_101_race_condition(self):
        # Generate a random ID so MySQL doesn't block duplicate emails/phones
        rand_id = random.randint(100000, 999999)
        
        # The payload that perfectly matches your HTML form
        payload = {
            "first_name": "Stress",
            "last_name": f"User_{rand_id}",
            "gender": "M",
            "age": 20,
            "contact": f"988{rand_id}",
            "email": f"stress_{rand_id}@stayease.com",
            "emergency_contact": "9999999999",
            "role_id": 1,
            "hostel_id": 2,
            "room_number": "101"  
        }

        # Passing your Admin token so Flask lets us in
        # Passing your Admin token exactly how Flask expects it
        headers = {"Authorization": f"Bearer {self.admin_token}"} 

        # Fire the JSON request at the server
        with self.client.post("/admin/members", json=payload, headers=headers, catch_response=True) as response:
            if response.status_code == 201:
                response.success()
            elif response.status_code == 400 and "is full" in response.text:
                # We expect 95 of these, so it counts as a successful test!
                response.success() 
            else:
                response.failure(f"Failed! Code: {response.status_code} - {response.text}")