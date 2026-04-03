from db_manager import DatabaseManager

# Initialize the Coordinator
db_admin = DatabaseManager()
db_admin.create_database("stayease")

# 1. Full Members Schema
# Maps to: Member_ID, First_Name, Last_Name, Gender, Age, Contact, Email, etc.
members_schema = {
    'Member_ID': int,
    'First_Name': str,
    'Last_Name': str,
    'Gender': str,
    'Age': int,
    'Contact_Number': str,
    'Email': str,
    'Emergency_Contact': str,
    'Image_Path': str,
    'Role_ID': int,
    'Status': str
}

# 2. Full Rooms Schema
# Maps to: Room_ID, Room_Number, Hostel_ID, Floor_Number, Capacity
rooms_schema = {
    'Room_ID': int,
    'Room_Number': str,
    'Hostel_ID': int,
    'Floor_Number': int,
    'Capacity': int
}

# 3. Full Room_Allocations Schema
# Maps to: Allocation_ID, Member_ID, Room_ID, Allocation_Date, Check_Out_Date, Status
allocations_schema = {
    'Allocation_ID': int,
    'Member_ID': int,
    'Room_ID': int,
    'Allocation_Date': str,  # Stored as 'YYYY-MM-DD'
    'Check_Out_Date': str,   # Stored as 'YYYY-MM-DD' or None
    'Status': str
}

# Create the tables in the Database Manager
db_admin.create_table("stayease", "members", members_schema, search_key="Member_ID")
db_admin.create_table("stayease", "rooms", rooms_schema, search_key="Room_ID")
db_admin.create_table("stayease", "room_allocations", allocations_schema, search_key="Allocation_ID")

# 4. Try to load existing data from disk [cite: 97, 99]
# If you've run this before, this will fill your B+ Trees with saved records.
db_admin.reload_all("stayease")

db_admin.recover("stayease")

# 5. Insert Seed Data (Optional - Only if not already there)
# This simulates your SQL dump records
members_table, msg = db_admin.get_table("stayease", "members")
rooms_table, _ = db_admin.get_table("stayease", "rooms")
alloc_table, _ = db_admin.get_table("stayease", "room_allocations")

if not members_table.get(110)[0] or not rooms_table.get(101)[0] or not members_table.get(112)[0]:
    db_admin.begin()
    if not members_table.get(110)[0]:
        priya = {
            'Member_ID': 110, 'First_Name': 'Priya', 'Last_Name': 'Sharma',
            'Gender': 'F', 'Age': 20, 'Contact_Number': '8888800001',
            'Email': 'priya@student.com', 'Status': 'Active',
            'Role_ID': 1, 'Image_Path': 'uploads/default.jpg', 'Emergency_Contact': '7777700001'
        }
        members_table.insert(priya)
        print("Seed data inserted: Member 110")
    if not members_table.get(112)[0]:
        ravi = {
            'Member_ID': 112, 'First_Name': 'Ravi', 'Last_Name': 'Kumar',
            'Gender': 'M', 'Age': 22, 'Contact_Number': '8888800002',
            'Email': 'ravi@student.com', 'Status': 'Active',
            'Role_ID': 1, 'Image_Path': 'uploads/default.jpg', 'Emergency_Contact': '7777700002'
        }
        members_table.insert(ravi)
        print("Seed data inserted: Member 112")
    if not rooms_table.get(101)[0]:
        room_data = {
            'Room_ID': 101, 'Room_Number': '101', 'Hostel_ID': 2,
            'Floor_Number': 1, 'Capacity': 2
        }
        rooms_table.insert(room_data)
        print("Seed data inserted: Room 101")
    db_admin.commit("stayease")

# 6. Save everything to disk
# This ensures that even if you stop the script now, the data is safe in .tree files.
db_admin.persist_all("stayease")

print("Database is ready and persistent.")