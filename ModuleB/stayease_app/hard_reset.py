# hard_reset.py
import os
from db_manager import DatabaseManager
from transaction_manager import TransactionManager

def reset_database():
    print("--- STAYEASE DATABASE RESET ---")
    
    # 1. Clean up old files
    for f in ["db_snapshot.pkl", "db_snapshot.pkl.bak", "stayease_wal.log", "stayease_db.pkl"]:
        if os.path.exists(f):
            os.remove(f)
            
    print("Initializing fresh database engine...")
    db = DatabaseManager()
    db.create_database("stayease")

    # 2. Build Tables
    tables = [
        ("roles", {"Role_ID": int, "Role_Name": str, "Description": str}, "Role_ID"),
        ("members", {"Member_ID": int, "First_Name": str, "Last_Name": str, "Gender": str, "Age": int, "Contact_Number": str, "Email": str, "Password": str, "Emergency_Contact": str, "Image_Path": str, "Role_ID": int, "Status": str}, "Member_ID"),
        ("hostels", {"Hostel_ID": int, "Hostel_Name": str, "Hostel_Type": str, "Total_Floors": int, "Warden_ID": int}, "Hostel_ID"),
        ("rooms", {"Room_ID": int, "Room_Number": str, "Hostel_ID": int, "Floor_Number": int, "Capacity": int}, "Room_ID"),
        ("room_allocations", {"Allocation_ID": int, "Member_ID": int, "Room_ID": int, "Allocation_Date": str, "Check_Out_Date": str, "Status": str}, "Allocation_ID"),
        ("furniture_inventory", {"Furniture_ID": int, "Item_Name": str, "Room_ID": int, "Purchase_Date": str, "Current_Condition": str}, "Furniture_ID"),
        ("visitor_logs", {"Log_ID": int, "Visitor_Name": str, "Contact_Number": str, "ID_Proof_Type": str, "ID_Proof_Number": str, "Host_Member_ID": int, "Entry_Time": str, "Purpose": str}, "Log_ID"),
        ("member_movement_logs", {"Movement_ID": int, "Member_ID": int, "Exit_Time": str, "Entry_Time": str, "Purpose": str}, "Movement_ID"),
        ("fee_structures", {"Fee_Type_ID": int, "Fee_Name": str, "Amount": float, "Academic_Year": str}, "Fee_Type_ID"),
        ("payments", {"Payment_ID": int, "Member_ID": int, "Fee_Type_ID": int, "Payment_Date": str, "Amount_Paid": float, "Payment_Status": str, "Transaction_Reference": str}, "Payment_ID"),
        ("complaint_types", {"Complaint_Type_ID": int, "Type_Name": str, "Sub_Type": str}, "Complaint_Type_ID"),
        ("complaints", {"Complaint_ID": int, "Member_ID": int, "Complaint_Type_ID": int, "Description": str, "Submission_Date": str, "Resolved_Date": str, "Status": str}, "Complaint_ID")
    ]

    for name, schema, key in tables:
        db.create_table("stayease", name, schema, order=8, search_key=key)

    tm = TransactionManager(db, "stayease", log_file="stayease_wal.log")
    txn = tm.begin_transaction()

    # --- INJECTING MASSIVE DATA ---

    # 1. Roles
    tm.insert(txn, "roles", 1, {"Role_ID": 1, "Role_Name": "Student", "Description": "Resident"})
    tm.insert(txn, "roles", 2, {"Role_ID": 2, "Role_Name": "Warden", "Description": "Manager"})
    tm.insert(txn, "roles", 3, {"Role_ID": 3, "Role_Name": "Admin", "Description": "System Admin"})

    # 2. Admin & Wardens
    tm.insert(txn, "members", 100, {"Member_ID": 100, "First_Name": "Super", "Last_Name": "Admin", "Gender": "M", "Age": 45, "Contact_Number": "9999999999", "Email": "admin@stayease.com", "Password": "password123", "Emergency_Contact": "9999999998", "Image_Path": "default.png", "Role_ID": 3, "Status": "Active"})
    
    wardens = [
        (101, "Riya", "Patel", "F", 32, "warden1@stayease.com"), # Manages Yamuna Girls
        (102, "Vikram", "Singh", "M", 40, "warden2@stayease.com"), # Manages Ganga Boys
        (103, "Sunita", "Desai", "F", 38, "warden3@stayease.com"), # Manages Saraswati Girls
        (104, "Rahul", "Verma", "M", 42, "warden4@stayease.com")   # Manages Narmada Boys
    ]
    for w in wardens:
        tm.insert(txn, "members", w[0], {"Member_ID": w[0], "First_Name": w[1], "Last_Name": w[2], "Gender": w[3], "Age": w[4], "Contact_Number": f"9876500{w[0]}", "Email": w[5], "Password": "password123", "Emergency_Contact": "0000000000", "Image_Path": "default.png", "Role_ID": 2, "Status": "Active"})

    # 3. Hostels
    tm.insert(txn, "hostels", 1, {"Hostel_ID": 1, "Hostel_Name": "Yamuna Girls Hostel", "Hostel_Type": "Girls", "Total_Floors": 3, "Warden_ID": 101})
    tm.insert(txn, "hostels", 2, {"Hostel_ID": 2, "Hostel_Name": "Ganga Boys Hostel", "Hostel_Type": "Boys", "Total_Floors": 4, "Warden_ID": 102})
    tm.insert(txn, "hostels", 3, {"Hostel_ID": 3, "Hostel_Name": "Saraswati Girls Hostel", "Hostel_Type": "Girls", "Total_Floors": 2, "Warden_ID": 103})
    tm.insert(txn, "hostels", 4, {"Hostel_ID": 4, "Hostel_Name": "Narmada Boys Hostel", "Hostel_Type": "Boys", "Total_Floors": 3, "Warden_ID": 104})

    # 4. Rooms
    rooms = [
        # Yamuna (Hostel 1)
        (201, "201", 1, 2, 2), (202, "202", 1, 2, 2),
        # Ganga (Hostel 2)
        (101, "101", 2, 1, 3), (102, "102", 2, 1, 2),
        # Saraswati (Hostel 3)
        (301, "301", 3, 1, 2),
        # Narmada (Hostel 4)
        (401, "401", 4, 1, 4)
    ]
    for r in rooms:
        tm.insert(txn, "rooms", r[0], {"Room_ID": r[0], "Room_Number": r[1], "Hostel_ID": r[2], "Floor_Number": r[3], "Capacity": r[4]})

    # 5. Students
    students = [
        # Girls
        (110, "Priya", "Sharma", "F", 20, "student1@stayease.com"),
        (111, "Ananya", "Gupta", "F", 19, "student2@stayease.com"),
        (112, "Kavita", "Rao", "F", 21, "student3@stayease.com"),
        (113, "Sneha", "Iyer", "F", 20, "student4@stayease.com"),
        (114, "Pooja", "Joshi", "F", 19, "unallocated1@stayease.com"), # Unallocated!
        (115, "Meera", "Reddy", "F", 22, "unallocated2@stayease.com"), # Unallocated!
        # Boys
        (116, "Amit", "Kumar", "M", 20, "student5@stayease.com"),
        (117, "Rohan", "Das", "M", 21, "student6@stayease.com"),
        (118, "Karan", "Malhotra", "M", 19, "student7@stayease.com"),
        (119, "Arjun", "Nair", "M", 20, "student8@stayease.com"),
        (120, "Yash", "Singhania", "M", 22, "student9@stayease.com"),
        (121, "Dev", "Patel", "M", 19, "unallocated3@stayease.com") # Unallocated!
    ]
    for s in students:
        tm.insert(txn, "members", s[0], {"Member_ID": s[0], "First_Name": s[1], "Last_Name": s[2], "Gender": s[3], "Age": s[4], "Contact_Number": f"8888800{s[0]}", "Email": s[5], "Password": "password123", "Emergency_Contact": "0000000000", "Image_Path": "default.png", "Role_ID": 1, "Status": "Active"})

    # 6. Room Allocations (Assigning most students to rooms)
    allocations = [
        (1, 110, 201), (2, 111, 201), # Priya and Ananya in Yamuna 201 (Full)
        (3, 112, 202),                # Kavita in Yamuna 202 (1 spot left)
        (4, 113, 301),                # Sneha in Saraswati 301 (1 spot left)
        (5, 116, 101), (6, 117, 101), # Amit and Rohan in Ganga 101 (1 spot left)
        (7, 118, 102),                # Karan in Ganga 102 (1 spot left)
        (8, 119, 401), (9, 120, 401)  # Arjun and Yash in Narmada 401 (2 spots left)
    ]
    for a in allocations:
        tm.insert(txn, "room_allocations", a[0], {"Allocation_ID": a[0], "Member_ID": a[1], "Room_ID": a[2], "Allocation_Date": "2026-01-10", "Check_Out_Date": "None", "Status": "Active"})

    # 7. Complaint Types & Fees
    tm.insert(txn, "complaint_types", 1, {"Complaint_Type_ID": 1, "Type_Name": "Plumbing", "Sub_Type": "Water Leakage"})
    tm.insert(txn, "complaint_types", 2, {"Complaint_Type_ID": 2, "Type_Name": "Electrical", "Sub_Type": "Fan/Light Not Working"})
    tm.insert(txn, "complaint_types", 3, {"Complaint_Type_ID": 3, "Type_Name": "Civil", "Sub_Type": "Broken Window"})
    tm.insert(txn, "complaint_types", 4, {"Complaint_Type_ID": 4, "Type_Name": "IT", "Sub_Type": "Wi-Fi Issue"})
    tm.insert(txn, "complaint_types", 5, {"Complaint_Type_ID": 5, "Type_Name": "Cleaning", "Sub_Type": "Room Not Cleaned"})
    tm.insert(txn, "complaint_types", 6, {"Complaint_Type_ID": 6, "Type_Name": "Cleaning", "Sub_Type": "Washroom Dirty"})
    tm.insert(txn, "complaint_types", 7, {"Complaint_Type_ID": 7, "Type_Name": "Food/Mess", "Sub_Type": "Poor Quality"})
    tm.insert(txn, "complaint_types", 8, {"Complaint_Type_ID": 8, "Type_Name": "Security", "Sub_Type": "Harassment/Safety"})
    tm.insert(txn, "complaint_types", 9, {"Complaint_Type_ID": 9, "Type_Name": "Furniture", "Sub_Type": "Broken Bed/Chair"})

    # 8. Fees
    tm.insert(txn, "fee_structures", 1, {"Fee_Type_ID": 1, "Fee_Name": "Semester Hostel Rent", "Amount": 25000.0, "Academic_Year": "2025-2026"})
    tm.insert(txn, "fee_structures", 2, {"Fee_Type_ID": 2, "Fee_Name": "Gym Membership", "Amount": 2000.0, "Academic_Year": "2025-2026"})
    tm.insert(txn, "fee_structures", 3, {"Fee_Type_ID": 3, "Fee_Name": "Late Fines", "Amount": 500.0, "Academic_Year": "2025-2026"})

    # 9. Test Movement Logs
    tm.insert(txn, "member_movement_logs", 1, {"Movement_ID": 1, "Member_ID": 110, "Exit_Time": "2026-04-03 18:00:00", "Entry_Time": "2026-04-03 21:00:00", "Purpose": "Market Visit"})
    tm.insert(txn, "member_movement_logs", 2, {"Movement_ID": 2, "Member_ID": 117, "Exit_Time": "2026-04-04 08:00:00", "Entry_Time": "None", "Purpose": "Going Home"})

    tm.commit(txn)
    print("--- VERIFICATION ---")
    print("Database reset complete. All test data has been injected.")

if __name__ == "__main__":
    reset_database()