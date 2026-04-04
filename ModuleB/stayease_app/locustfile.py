from locust import HttpUser, task, between
import random

class StayEaseLoadTest(HttpUser):
    # Simulate realistic user "think time" between clicks (1 to 3 seconds)
    wait_time = between(1, 3)

    def on_start(self):
        """This runs once when a simulated user 'boots up'."""
        # Pick a random student from your database to log in as
        student_id = random.randint(110, 119)
        email = f"student{student_id - 109}@stayease.com" 
        
        # Log in
        self.client.post("/", data={"email": email, "password": "password123"})

    @task(3)
    def view_student_dashboard(self):
        """Simulate the user refreshing or viewing their dashboard. (Runs 3x more often)"""
        self.client.get("/student_dashboard")

    @task(1)
    def submit_random_complaint(self):
        """Simulate the user submitting a complaint."""
        self.client.post("/submit_complaint", data={
            "subcategory": random.randint(1, 4), # Random issue type
            "description": "Locust Automated Load Test Complaint"
        })