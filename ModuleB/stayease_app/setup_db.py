# setup_db.py
from db_manager import DatabaseManager
from transaction_manager import TransactionManager

def initialize_database():
    print("Initializing Full StayEase Database Engine...")
    db = DatabaseManager()
    
    # Create the main database
    success, msg = db.create_database("stayease")
    print(msg)

    # 1. Roles
    db.create_table("stayease", "roles", 
                    schema={"Role_ID": int, "Role_Name": str, "Description": str}, 
                    order=8, search_key="Role_ID")

    # 2. Members
    db.create_table("stayease", "members", 
                    schema={"Member_ID": int, "First_Name": str, "Last_Name": str, 
                            "Gender": str, "Age": int, "Contact_Number": str, 
                            "Email": str, "Emergency_Contact": str, 
                            "Image_Path": str, "Role_ID": int, "Status": str}, 
                    order=8, search_key="Member_ID")

    # 3. Hostels
    db.create_table("stayease", "hostels", 
                    schema={"Hostel_ID": int, "Hostel_Name": str, "Hostel_Type": str, 
                            "Total_Floors": int, "Warden_ID": int}, 
                    order=8, search_key="Hostel_ID")

    # 4. Rooms
    db.create_table("stayease", "rooms", 
                    schema={"Room_ID": int, "Room_Number": str, "Hostel_ID": int, 
                            "Floor_Number": int, "Capacity": int}, 
                    order=8, search_key="Room_ID")

    # 5. Room Allocations
    db.create_table("stayease", "room_allocations", 
                    schema={"Allocation_ID": int, "Member_ID": int, "Room_ID": int, 
                            "Allocation_Date": str, "Check_Out_Date": str, "Status": str}, 
                    order=8, search_key="Allocation_ID")

    # 6. Furniture Inventory
    db.create_table("stayease", "furniture_inventory", 
                    schema={"Furniture_ID": int, "Item_Name": str, "Room_ID": int, 
                            "Purchase_Date": str, "Current_Condition": str}, 
                    order=8, search_key="Furniture_ID")

    # 7. Visitor Logs
    db.create_table("stayease", "visitor_logs", 
                    schema={"Log_ID": int, "Visitor_Name": str, "Contact_Number": str, 
                            "ID_Proof_Type": str, "ID_Proof_Number": str, 
                            "Host_Member_ID": int, "Entry_Time": str, "Purpose": str}, 
                    order=8, search_key="Log_ID")

    # 8. Member Movement Logs
    db.create_table("stayease", "member_movement_logs", 
                    schema={"Movement_ID": int, "Member_ID": int, "Exit_Time": str, 
                            "Entry_Time": str, "Purpose": str}, 
                    order=8, search_key="Movement_ID")

    # 9. Fee Structures
    db.create_table("stayease", "fee_structures", 
                    schema={"Fee_Type_ID": int, "Fee_Name": str, "Amount": float, 
                            "Academic_Year": str}, 
                    order=8, search_key="Fee_Type_ID")

    # 10. Payments
    db.create_table("stayease", "payments", 
                    schema={"Payment_ID": int, "Member_ID": int, "Fee_Type_ID": int, 
                            "Payment_Date": str, "Amount_Paid": float, 
                            "Payment_Status": str, "Transaction_Reference": str}, 
                    order=8, search_key="Payment_ID")

    # 11. Complaint Types
    db.create_table("stayease", "complaint_types", 
                    schema={"Complaint_Type_ID": int, "Type_Name": str, "Sub_Type": str}, 
                    order=8, search_key="Complaint_Type_ID")

    # 12. Complaints
    db.create_table("stayease", "complaints", 
                    schema={"Complaint_ID": int, "Member_ID": int, "Complaint_Type_ID": int, 
                            "Description": str, "Submission_Date": str, 
                            "Resolved_Date": str, "Status": str}, 
                    order=8, search_key="Complaint_ID")

    print("All 12 tables created successfully!")

    # Initialize Transaction Manager to insert test data safely
    tm = TransactionManager(db, "stayease", log_file="stayease_wal.log")
    txn = tm.begin_transaction()

    # Insert Roles
    tm.insert(txn, "roles", 1, {"Role_ID": 1, "Role_Name": "Student", "Description": "Resident"})
    tm.insert(txn, "roles", 2, {"Role_ID": 2, "Role_Name": "Warden", "Description": "Manager"})
    tm.insert(txn, "roles", 3, {"Role_ID": 3, "Role_Name": "Admin", "Description": "System Admin"})

    # Insert Test Users (Email is the username)
    tm.insert(txn, "members", 110, {
        "Member_ID": 110, "First_Name": "Priya", "Last_Name": "Sharma", "Gender": "F", "Age": 20, 
        "Contact_Number": "8888800001", "Email": "student@stayease.com", "Password": "password123", 
        "Emergency_Contact": "7777700001", "Image_Path": "default.png", "Role_ID": 1, "Status": "Active"
    })
    
    tm.insert(txn, "members", 102, {
        "Member_ID": 102, "First_Name": "Riya", "Last_Name": "Patel", "Gender": "F", "Age": 32, 
        "Contact_Number": "9876500002", "Email": "warden@stayease.com", "Password": "password123", 
        "Emergency_Contact": "9876500003", "Image_Path": "default.png", "Role_ID": 2, "Status": "Active"
    })

    tm.insert(txn, "members", 100, {
        "Member_ID": 100, "First_Name": "Super", "Last_Name": "Admin", "Gender": "M", "Age": 45, 
        "Contact_Number": "9999999999", "Email": "admin@stayease.com", "Password": "password123", 
        "Emergency_Contact": "9999999998", "Image_Path": "default.png", "Role_ID": 3, "Status": "Active"
    })

    # Insert Fee Structures
    tm.insert(txn, "fee_structures", 1, {"Fee_Type_ID": 1, "Fee_Name": "Semester Hostel Rent", "Amount": 25000.0, "Academic_Year": "2025-2026"})
    tm.insert(txn, "fee_structures", 2, {"Fee_Type_ID": 2, "Fee_Name": "Gym Membership", "Amount": 2000.0, "Academic_Year": "2025-2026"})

    tm.commit(txn)
    print("Database snapshot and test users saved to stayease_db.pkl")

    # # Save the empty database structure to disk
    # db.save_to_disk("stayease_db.pkl")
    # print("Database snapshot saved to stayease_db.pkl")

if __name__ == "__main__":
    initialize_database()