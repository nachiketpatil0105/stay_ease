# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from db_manager import DatabaseManager
from transaction_manager import TransactionManager
import datetime
import uuid

app = Flask(__name__)
# Secret key is required to use Flask 'session' and 'flash' features securely
app.secret_key = "stayease_secure_key_123" 

# --- Database Initialization ---
db = DatabaseManager()
# Use the default filename that the TransactionManager creates
if not db.load_from_disk("db_snapshot.pkl"): 
    print("WARNING: Database snapshot not found.")
tm = TransactionManager(db, "stayease", log_file="stayease_wal.log")

# --- Routes ---

@app.route('/', methods=['GET', 'POST'])
def login():
    # If the user submits the login form
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Retrieve the members table from the DatabaseManager
        members_table, msg = db.get_table("stayease", "members")
        if not members_table:
            flash(f"System Error: {msg}") # This will print the exact reason it failed!
            return render_template('login.html')

        # Get all records from the B+ Tree
        all_members = members_table.get_all()
        
        # Scan through the B+ Tree linked-list to find the user
        for member_id, record in all_members:
            if record.get('Email') == email and record.get('Password') == password:
                # Login Successful! Store user data in the session dictionary
                session['member_id'] = member_id
                session['name'] = record.get('First_Name')
                session['role_id'] = record.get('Role_ID')

                # Route them to the correct dashboard based on their Role_ID
                if session['role_id'] == 1:
                    return redirect(url_for('student_dashboard'))
                elif session['role_id'] == 2:
                    return redirect(url_for('warden_dashboard'))
                elif session['role_id'] == 3:
                    return redirect(url_for('admin_dashboard'))

        # If loop finishes and no match is found
        flash("Invalid email or password.")
        return redirect(url_for('login'))

    # If it's a GET request, just show the login page
    return render_template('login.html')


@app.route('/student_dashboard')
def student_dashboard():
    if 'member_id' not in session or session.get('role_id') != 1:
        return redirect(url_for('login'))

    member_id = session['member_id']
    
    # 1. Fetch the student's room allocation (WITH SAFETY CHECK)
    alloc_table, _ = db.get_table("stayease", "room_allocations")
    my_room_id = None
    if alloc_table: # <--- Fixes the Pylance 'None' error
        for alloc_id, record in alloc_table.get_all():
            if record['Member_ID'] == member_id and record['Status'] == 'Active':
                my_room_id = record['Room_ID']
                break
            
    # 2. Fetch room details
    my_room = None
    if my_room_id:
        room_table, _ = db.get_table("stayease", "rooms")
        if room_table: # <--- Fixes the Pylance 'data' error
            my_room = room_table.data.search(my_room_id)

    # 3. Fetch past complaints
    my_complaints = []
    comp_table, _ = db.get_table("stayease", "complaints")
    if comp_table:
        my_complaints = [record for _, record in comp_table.get_all() if record['Member_ID'] == member_id]
            
    # 4. Fetch and GROUP complaint categories
    complaint_dict = {}
    type_table, _ = db.get_table("stayease", "complaint_types")
    if type_table:
        for _, record in type_table.get_all():
            category = record['Type_Name']
            if category not in complaint_dict:
                complaint_dict[category] = []
            complaint_dict[category].append({"id": record['Complaint_Type_ID'], "sub": record['Sub_Type']})

    # 5. Fetch Fee Structures & Past Payments
    available_fees = []
    fee_table, _ = db.get_table("stayease", "fee_structures")
    if fee_table:
        for _, record in fee_table.get_all():
            if record['Fee_Name'] == "Semester Hostel Rent":
                available_fees.append(record)

    my_payments = []
    payment_table, _ = db.get_table("stayease", "payments")
    if payment_table:
        for _, record in payment_table.get_all():
            if record['Member_ID'] == member_id:
                fee_name = next((f['Fee_Name'] for f in available_fees if f['Fee_Type_ID'] == record['Fee_Type_ID']), "Unknown Fee")
                record['Fee_Name'] = fee_name
                my_payments.append(record)

    return render_template('student_dashboard.html', 
                           name=session.get('name'), 
                           room=my_room, 
                           complaints=my_complaints,
                           complaint_dict=complaint_dict,
                           available_fees=available_fees,
                           my_payments=my_payments)


@app.route('/submit_complaint', methods=['POST'])
def submit_complaint():
    if 'member_id' not in session or session.get('role_id') != 1:
        return redirect(url_for('login'))

    member_id = session['member_id']
    comp_type_str = request.form.get('subcategory')
    if not comp_type_str:
        flash("Please select a valid subcategory.")
        return redirect(url_for('student_dashboard'))
        
    comp_type = int(comp_type_str)
    description = request.form.get('description')

    # THE FIX: Start the transaction FIRST
    txn = tm.begin_transaction()
    try:
        # Manually acquire the write-lock for this table BEFORE reading the IDs.
        # This forces the 5 simultaneous threads into a strict, single-file line!
        tm._acquire_lock(txn, "complaints") 

        # Now it is safe to calculate the ID, because no one else can read/write
        # while we hold the lock.
        comp_table, _ = db.get_table("stayease", "complaints")
        existing_ids = [k for k, v in comp_table.get_all()] if comp_table else []
        new_id = max(existing_ids + [0]) + 1

        # Insert the data
        tm.insert(txn, "complaints", new_id, {
            "Complaint_ID": new_id, "Member_ID": member_id, "Complaint_Type_ID": comp_type,
            "Description": description, "Submission_Date": datetime.date.today().strftime("%Y-%m-%d"),
            "Resolved_Date": "None", "Status": "Pending"
        })
        
        # Committing releases the lock so the next thread in line can calculate its ID!
        tm.commit(txn)
        flash("Complaint submitted successfully!")
    except Exception as e:
        tm.rollback(txn)
        flash(f"Error submitting complaint: {e}")

    return redirect(url_for('student_dashboard'))


@app.route('/pay_fee', methods=['POST'])
def pay_fee():
    if 'member_id' not in session or session.get('role_id') != 1:
        return redirect(url_for('login'))

    member_id = session['member_id']
    
    # SAFETY CHECK: Fixes the 'ConvertibleToInt' error
    fee_id_str = request.form.get('fee_id')
    if not fee_id_str:
        flash("Please select a valid fee to pay.")
        return redirect(url_for('student_dashboard'))
        
    fee_type_id = int(fee_id_str)

    fee_table, _ = db.get_table("stayease", "fee_structures")
    fee_record = fee_table.data.search(fee_type_id) if fee_table else None
    
    if not fee_record:
        flash("Invalid fee selected.")
        return redirect(url_for('student_dashboard'))

    payment_table, _ = db.get_table("stayease", "payments")
    existing_ids = [k for k, v in payment_table.get_all()] if payment_table else []
    new_id = max(existing_ids + [0]) + 1
    txn_ref = f"TXN-{str(uuid.uuid4())[:8].upper()}"

    txn = tm.begin_transaction()
    try:
        tm.insert(txn, "payments", new_id, {
            "Payment_ID": new_id, "Member_ID": member_id, "Fee_Type_ID": fee_type_id,
            "Payment_Date": datetime.date.today().strftime("%Y-%m-%d"),
            "Amount_Paid": fee_record['Amount'], "Payment_Status": "Success",
            "Transaction_Reference": txn_ref
        })
        tm.commit(txn)
        flash(f"Payment of ₹{fee_record['Amount']} successful! Reference: {txn_ref}")
    except Exception as e:
        tm.rollback(txn)
        flash(f"Payment failed: {e}")

    return redirect(url_for('student_dashboard'))

@app.route('/warden_dashboard')
def warden_dashboard():
    if 'member_id' not in session or session.get('role_id') != 2: return redirect(url_for('login'))
    warden_id = session['member_id']

    # Keep all existing logic exactly the same...
    hostel_table, _ = db.get_table("stayease", "hostels")
    my_hostel = next((r for _, r in hostel_table.get_all() if r['Warden_ID'] == warden_id), None) if hostel_table else None
    if not my_hostel: return render_template('warden_dashboard.html', name=session.get('name'), error="No hostel assigned.")

    room_table, _ = db.get_table("stayease", "rooms")
    hostel_rooms = [r for _, r in room_table.get_all() if r['Hostel_ID'] == my_hostel['Hostel_ID']] if room_table else []
    my_room_ids = [r['Room_ID'] for r in hostel_rooms]
    room_capacities = {r['Room_ID']: r['Capacity'] for r in hostel_rooms}
    room_occupancy = {r['Room_ID']: 0 for r in hostel_rooms}

    alloc_table, _ = db.get_table("stayease", "room_allocations")
    active_allocs = [a for _, a in alloc_table.get_all() if a['Status'] == 'Active'] if alloc_table else []
    
    hostel_student_ids, all_allocated_student_ids = [], []
    for alloc in active_allocs:
        all_allocated_student_ids.append(alloc['Member_ID'])
        if alloc['Room_ID'] in room_capacities:
            room_occupancy[alloc['Room_ID']] += 1
            hostel_student_ids.append(alloc['Member_ID'])

    available_rooms = [{'Room_ID': r['Room_ID'], 'Room_Number': r['Room_Number'], 'Available_Spots': r['Capacity'] - room_occupancy[r['Room_ID']]} for r in hostel_rooms if room_occupancy[r['Room_ID']] < r['Capacity']]

    member_table, _ = db.get_table("stayease", "members")
    all_students = [m for _, m in member_table.get_all() if m['Role_ID'] == 1] if member_table else []
    unallocated_students = [s for s in all_students if s['Member_ID'] not in all_allocated_student_ids]
    
    current_residents = []
    for s in all_students:
        if s['Member_ID'] in hostel_student_ids:
            alloc = next((a for a in active_allocs if a['Member_ID'] == s['Member_ID']), None)
            room_num = next((r['Room_Number'] for r in hostel_rooms if r['Room_ID'] == alloc['Room_ID']), "Unknown")
            current_residents.append({'Member_ID': s['Member_ID'], 'Name': f"{s['First_Name']} {s['Last_Name']}", 'Email': s['Email'], 'Room_Number': room_num, 'Allocation_Date': alloc['Allocation_Date']})

    type_table, _ = db.get_table("stayease", "complaint_types")
    types_dict = {t['Complaint_Type_ID']: f"{t['Type_Name']} - {t['Sub_Type']}" for _, t in type_table.get_all()} if type_table else {}

    comp_table, _ = db.get_table("stayease", "complaints")
    hostel_complaints = []
    if comp_table:
        for _, c in comp_table.get_all():
            if c['Member_ID'] in hostel_student_ids:
                student = next((s for s in all_students if s['Member_ID'] == c['Member_ID']), None)
                c['Student_Name'] = f"{student['First_Name']} {student['Last_Name']}" if student else "Unknown"
                c['Issue_Type'] = types_dict.get(c['Complaint_Type_ID'], "Unknown Issue")
                hostel_complaints.append(c)

    furn_table, _ = db.get_table("stayease", "furniture_inventory")
    hostel_furniture = []
    if furn_table:
        for _, f in furn_table.get_all():
            if f['Room_ID'] in my_room_ids:
                room_num = next((r['Room_Number'] for r in hostel_rooms if r['Room_ID'] == f['Room_ID']), "Unknown")
                f['Room_Number'] = room_num
                hostel_furniture.append(f)

    vis_table, _ = db.get_table("stayease", "visitor_logs")
    hostel_visitors = []
    if vis_table:
        for _, v in vis_table.get_all():
            if v['Host_Member_ID'] in hostel_student_ids:
                host = next((s for s in all_students if s['Member_ID'] == v['Host_Member_ID']), None)
                v['Host_Name'] = f"{host['First_Name']} {host['Last_Name']}" if host else "Unknown"
                hostel_visitors.append(v)

    # ADDED: Fetch Movement Logs for this Warden's Hostel
    move_table, _ = db.get_table("stayease", "member_movement_logs")
    hostel_movement = []
    if move_table:
        for _, m in move_table.get_all():
            if m['Member_ID'] in hostel_student_ids:
                student = next((s for s in all_students if s['Member_ID'] == m['Member_ID']), None)
                m['Student_Name'] = f"{student['First_Name']} {student['Last_Name']}" if student else "Unknown"
                hostel_movement.append(m)

    return render_template('warden_dashboard.html', name=session.get('name'), hostel=my_hostel, complaints=hostel_complaints,
                           current_residents=current_residents, available_rooms=available_rooms,
                           unallocated_students=unallocated_students, furniture=hostel_furniture, 
                           visitors=hostel_visitors, movement=hostel_movement)


@app.route('/allocate_student', methods=['POST'])
def allocate_student():
    if 'member_id' not in session or session.get('role_id') != 2:
        return redirect(url_for('login'))

    student_id_str = request.form.get('student_id')
    room_id_str = request.form.get('room_id')

    if not student_id_str or not room_id_str:
        flash("Please select both a student and a room.")
        return redirect(url_for('warden_dashboard'))

    student_id = int(student_id_str)
    room_id = int(room_id_str)

    alloc_table, _ = db.get_table("stayease", "room_allocations")
    existing_ids = [k for k, v in alloc_table.get_all()] if alloc_table else []
    new_id = max(existing_ids + [0]) + 1

    txn = tm.begin_transaction()
    try:
        tm.insert(txn, "room_allocations", new_id, {
            "Allocation_ID": new_id,
            "Member_ID": student_id,
            "Room_ID": room_id,
            "Allocation_Date": datetime.date.today().strftime("%Y-%m-%d"),
            "Check_Out_Date": "None",
            "Status": "Active"
        })
        tm.commit(txn)
        flash("Student successfully allocated to room!")
    except Exception as e:
        tm.rollback(txn)
        flash(f"Error allocating student: {e}")

    return redirect(url_for('warden_dashboard'))


@app.route('/update_complaint/<int:complaint_id>', methods=['POST'])
def update_complaint(complaint_id):
    """Allows the Warden to change a complaint's status."""
    if 'member_id' not in session or session.get('role_id') != 2:
        return redirect(url_for('login'))
        
    new_status = request.form.get('status')
    comp_table, _ = db.get_table("stayease", "complaints")
    
    if comp_table:
        # Search the B+ Tree for the specific complaint
        record = comp_table.data.search(complaint_id)
        if record:
            txn = tm.begin_transaction()
            try:
                # Update the record dictionary
                record['Status'] = new_status
                if new_status == 'Resolved':
                    record['Resolved_Date'] = datetime.date.today().strftime("%Y-%m-%d")
                
                # Push the update to the B+ Tree
                tm.update(txn, "complaints", complaint_id, record)
                tm.commit(txn)
                flash(f"Complaint #{complaint_id} successfully marked as {new_status}!")
            except Exception as e:
                tm.rollback(txn)
                flash(f"Error updating complaint: {e}")
                
    return redirect(url_for('warden_dashboard'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'member_id' not in session or session.get('role_id') != 3: return redirect(url_for('login'))

    # 1. Base Stats
    payment_table, _ = db.get_table("stayease", "payments")
    total_revenue = sum(p['Amount_Paid'] for _, p in payment_table.get_all() if p['Payment_Status'] == 'Success') if payment_table else 0

    member_table, _ = db.get_table("stayease", "members")
    all_members = [m for _, m in member_table.get_all()] if member_table else []
    total_students = len([m for m in all_members if m['Role_ID'] == 1])
    member_dict = {m['Member_ID']: f"{m['First_Name']} {m['Last_Name']}" for m in all_members}

    # 2. Hostels
    hostel_table, _ = db.get_table("stayease", "hostels")
    all_hostels = []
    if hostel_table:
        for _, h in hostel_table.get_all():
            h['Warden_Name'] = member_dict.get(h['Warden_ID'], "Unassigned")
            all_hostels.append(h)

    # 3. Complaints
    comp_table, _ = db.get_table("stayease", "complaints")
    all_complaints = []
    pending_complaints = 0
    if comp_table:
        type_table, _ = db.get_table("stayease", "complaint_types")
        types_dict = {t['Complaint_Type_ID']: f"{t['Type_Name']} - {t['Sub_Type']}" for _, t in type_table.get_all()} if type_table else {}
        for _, c in comp_table.get_all():
            if c['Status'] == 'Pending': pending_complaints += 1
            c['Student_Name'] = member_dict.get(c['Member_ID'], "Unknown")
            c['Issue_Type'] = types_dict.get(c['Complaint_Type_ID'], "Unknown")
            all_complaints.append(c)

    # 4. Global Furniture, Visitors, and Movement
    furn_table, _ = db.get_table("stayease", "furniture_inventory")
    all_furniture = [f for _, f in furn_table.get_all()] if furn_table else []

    vis_table, _ = db.get_table("stayease", "visitor_logs")
    all_visitors = []
    if vis_table:
        for _, v in vis_table.get_all():
            v['Host_Name'] = member_dict.get(v['Host_Member_ID'], "Unknown")
            all_visitors.append(v)

    move_table, _ = db.get_table("stayease", "member_movement_logs")
    all_movement = []
    if move_table:
        for _, m in move_table.get_all():
            m['Student_Name'] = member_dict.get(m['Member_ID'], "Unknown")
            all_movement.append(m)

    return render_template('admin_dashboard.html', name=session.get('name'), total_revenue=total_revenue,
                           total_students=total_students, pending_complaints=pending_complaints, hostels=all_hostels,
                           all_members=all_members, all_complaints=all_complaints, all_furniture=all_furniture, 
                           all_visitors=all_visitors, all_movement=all_movement)

@app.route('/logout')
def logout():
    # Clear the session data to log out
    session.clear()
    return redirect(url_for('login'))

@app.route('/add_student', methods=['POST'])
def add_student():
    if 'member_id' not in session or session.get('role_id') not in [2, 3]: 
        return redirect(url_for('login'))
    
    member_table, _ = db.get_table("stayease", "members")
    existing_ids = [k for k, v in member_table.get_all()] if member_table else []
    new_id = max(existing_ids + [0]) + 1

    txn = tm.begin_transaction()
    try:
        tm.insert(txn, "members", new_id, {
            "Member_ID": new_id, "First_Name": request.form.get('first_name'), "Last_Name": request.form.get('last_name'),
            "Gender": request.form.get('gender'), "Age": int(request.form.get('age')), "Contact_Number": request.form.get('contact'),
            "Email": request.form.get('email'), "Password": "password123", "Emergency_Contact": request.form.get('emergency'),
            "Image_Path": "default.png", "Role_ID": 1, "Status": "Active"
        })
        tm.commit(txn)
        flash(f"Student {request.form.get('first_name')} registered successfully! Default password is 'password123'")
    except Exception as e:
        tm.rollback(txn)
        flash(f"Error adding student: {e}")
    return redirect(url_for('admin_dashboard'))

@app.route('/add_furniture', methods=['POST'])
def add_furniture():
    if 'member_id' not in session or session.get('role_id') != 2: return redirect(url_for('login'))
    
    furn_table, _ = db.get_table("stayease", "furniture_inventory")
    new_id = max([k for k, v in furn_table.get_all()] + [0]) + 1 if furn_table else 1
    
    txn = tm.begin_transaction()
    try:
        tm.insert(txn, "furniture_inventory", new_id, {
            "Furniture_ID": new_id, "Item_Name": request.form.get('item_name'), 
            "Room_ID": int(request.form.get('room_id')), "Purchase_Date": datetime.date.today().strftime("%Y-%m-%d"), 
            "Current_Condition": request.form.get('condition')
        })
        tm.commit(txn)
        flash("Property added to inventory successfully!")
    except Exception as e:
        tm.rollback(txn)
        flash(f"Error adding furniture: {e}")
    return redirect(url_for('warden_dashboard'))


@app.route('/log_visitor', methods=['POST'])
def log_visitor():
    if 'member_id' not in session or session.get('role_id') != 2: return redirect(url_for('login'))
    
    vis_table, _ = db.get_table("stayease", "visitor_logs")
    new_id = max([k for k, v in vis_table.get_all()] + [0]) + 1 if vis_table else 1
    
    txn = tm.begin_transaction()
    try:
        tm.insert(txn, "visitor_logs", new_id, {
            "Log_ID": new_id, "Visitor_Name": request.form.get('visitor_name'), 
            "Contact_Number": request.form.get('contact'), "ID_Proof_Type": request.form.get('id_type'), 
            "ID_Proof_Number": request.form.get('id_number'), "Host_Member_ID": int(request.form.get('host_id')), 
            "Entry_Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Purpose": request.form.get('purpose')
        })
        tm.commit(txn)
        flash("Visitor entry logged successfully!")
    except Exception as e:
        tm.rollback(txn)
        flash(f"Error logging visitor: {e}")
    return redirect(url_for('warden_dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)