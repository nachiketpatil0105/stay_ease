from flask import Blueprint, jsonify, request
from utils import get_db_connection, token_required, log_audit
import datetime

admin_bp = Blueprint('admin_routes', __name__)

# View Members (Role-Based Filtering)
@admin_bp.route('/admin/members', methods=['GET'])
@token_required
def get_all_members(current_user):
    req_username = current_user['username']
    req_role = current_user['role'].lower()
    member_id = current_user['member_id'] # Get the ID of the person logging in!
    
    if req_role not in ['admin', 'warden']:
        return jsonify({"error": "Admin access required."}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT m.Member_ID, m.First_Name, m.Last_Name, m.Email, m.Contact_Number, m.Status,
               h.Hostel_ID,h.Hostel_Name, r.Room_Number, ro.Role_Name
        FROM members m
        JOIN roles ro ON m.Role_ID = ro.Role_ID
        LEFT JOIN room_allocations ra ON m.Member_ID = ra.Member_ID AND ra.Status = 'Active'
        LEFT JOIN rooms r ON ra.Room_ID = r.Room_ID
        LEFT JOIN hostels h ON r.Hostel_ID = h.Hostel_ID
        WHERE ro.Role_Name = 'Student'
    """
    params = []

    # If the user is a Warden, restrict the view to their specific hostel!
    if req_role == 'warden':
        query += " AND h.Warden_ID = %s "
        params.append(member_id)
        
    query += " ORDER BY m.Member_ID DESC"
    
    cursor.execute(query, tuple(params))
    all_members = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify({"members": all_members}), 200


# View Complaints (Role-Based Filtering)
@admin_bp.route('/admin/complaints', methods=['GET'])
@token_required
def get_all_complaints(current_user):
    req_role = current_user['role'].lower()
    member_id = current_user['member_id']

    if req_role not in ['admin', 'warden']:
        return jsonify({"error": "Admin access required."}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT c.Complaint_ID, c.Description, c.Status, c.Submission_Date,
               ct.Type_Name, m.First_Name, m.Last_Name,
               h.Hostel_Name, r.Room_Number
        FROM complaints c
        JOIN complaint_types ct ON c.Complaint_Type_ID = ct.Complaint_Type_ID
        JOIN members m ON c.Member_ID = m.Member_ID
        LEFT JOIN room_allocations ra ON m.Member_ID = ra.Member_ID AND ra.Status = 'Active'
        LEFT JOIN rooms r ON ra.Room_ID = r.Room_ID
        LEFT JOIN hostels h ON r.Hostel_ID = h.Hostel_ID
    """
    params = []

    # If it's a Warden, then added a WHERE clause. (If it's an Admin, then left it blank to get everything!)
    if req_role == 'warden':
        query += " WHERE h.Warden_ID = %s "
        params.append(member_id)
        
    query += " ORDER BY c.Submission_Date DESC"
    
    cursor.execute(query, tuple(params))
    complaints = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify({"complaints": complaints}), 200


# Add New Member & Allocate Room
@admin_bp.route('/admin/members', methods=['POST'])
@token_required
def add_member(current_user):
    if current_user['role'].lower() not in ['admin', 'warden']:
        return jsonify({"error": "Admin access required."}), 403

    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) 

    try:
        # Starting the ACID Transaction
        conn.start_transaction() 

        # Verify the Room Exists and Check Capacity
        # also find the internal Room_ID using Hostel_ID and Room_Number
        room_number = data.get('room_number')
        hostel_id = data.get('hostel_id')
        
        capacity_query = """
            SELECT r.Room_ID, r.Capacity, 
                (SELECT COUNT(*) FROM room_allocations ra WHERE ra.Room_ID = r.Room_ID AND ra.Status = 'Active') as Occupied
            FROM rooms r
            WHERE r.Room_Number = %s AND r.Hostel_ID = %s
            FOR UPDATE
        """

        cursor.execute(capacity_query, (room_number, hostel_id))
        room_info = cursor.fetchone()

        if not room_info:
            conn.rollback()
            return jsonify({"error": f"Room {room_number} does not exist in Hostel {hostel_id}."}), 404

        if room_info['Occupied'] >= room_info['Capacity']:
            conn.rollback() 
            return jsonify({"error": f"Room {room_number} is full (Max Capacity: {room_info['Capacity']})."}), 400
        
        actual_room_id = room_info['Room_ID']


        # Insert the New Member
        member_query = """
            INSERT INTO members 
            (First_Name, Last_Name, Gender, Age, Contact_Number, Email, Emergency_Contact, Image_Path, Role_ID, Status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        member_values = (
    data.get('first_name'), 
    data.get('last_name', ''), 
    data.get('gender'), 
    data.get('age'), 
    data.get('contact'), 
    data.get('email'), 
    data.get('emergency_contact', ''), 
    data.get('image_path', 'uploads/default.png'), 
    data.get('role_id'), 
    'Active'
)
        cursor.execute(member_query, member_values)
        

        new_member_id = cursor.lastrowid 

        # Create the Room Allocation
        allocation_query = """
            INSERT INTO room_allocations (Member_ID, Room_ID, Allocation_Date, Status)
            VALUES (%s, %s, %s, %s)
        """
        current_date = datetime.date.today()
        cursor.execute(allocation_query, (new_member_id, actual_room_id, current_date, 'Active'))

        conn.commit()
        
        log_audit(current_user['username'], current_user['role'], f"Added member {new_member_id} to room {actual_room_id}")
        return jsonify({"message": "Member added and room allocated successfully!"}), 201

    except Exception as e:
        conn.rollback() # Undo on any unexpected SQL error
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()



# Update Member Details
@admin_bp.route('/admin/members/<int:member_id>', methods=['PUT'])
@token_required
def update_member(current_user, member_id):
    if current_user['role'].lower() not in ['admin', 'warden']:
        return jsonify({"error": "Admin access required."}), 403

    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Update Contact Number and Status
        query = "UPDATE members SET Contact_Number = %s, Status = %s WHERE Member_ID = %s"
        cursor.execute(query, (data['contact'], data['status'], member_id))
        conn.commit()
        
        log_audit(current_user['username'], current_user['role'], f"Updated Member ID: {member_id}")
        return jsonify({"message": "Member updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()



# Update Complaint Status
@admin_bp.route('/admin/complaints/<int:complaint_id>', methods=['PUT'])
@token_required
def update_complaint_status(current_user, complaint_id):
    if current_user['role'].lower() not in ['admin', 'warden']:
        return jsonify({"error": "Admin access required."}), 403

    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['Pending', 'In Progress', 'Resolved']:
        return jsonify({"error": "Invalid status value."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Handle the Resolved_Date based on the new status
        if new_status == 'Resolved':
            query = "UPDATE complaints SET Status = %s, Resolved_Date = CURRENT_DATE() WHERE Complaint_ID = %s"
        else:
            # If reverting to Pending/In Progress, then clear the date!
            query = "UPDATE complaints SET Status = %s, Resolved_Date = NULL WHERE Complaint_ID = %s"
            
        cursor.execute(query, (new_status, complaint_id))
        conn.commit()
        
        log_audit(current_user['username'], current_user['role'], f"Updated Complaint ID {complaint_id} to {new_status}")
        return jsonify({"message": "Complaint status updated!"}), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()



# Delete a Complaint
@admin_bp.route('/admin/complaints/<int:complaint_id>', methods=['DELETE'])
@token_required
def delete_complaint(current_user, complaint_id):
    if current_user['role'].lower() not in ['admin', 'warden']:
        return jsonify({"error": "Admin access required."}), 403

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = "DELETE FROM complaints WHERE Complaint_ID = %s"
        cursor.execute(query, (complaint_id,))
        conn.commit()
        
        log_audit(current_user['username'], current_user['role'], f"Deleted Complaint ID: {complaint_id}")
        return jsonify({"message": "Complaint deleted successfully!"}), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# Get Admin Stats
@admin_bp.route('/admin/stats', methods=['GET'])
@token_required
def get_admin_stats(current_user):
    if current_user['role'].lower() not in ['admin', 'warden']:
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Determine if we need to filter by Warden_ID
        warden_filter = ""
        params = ()
        if current_user['role'].lower() == 'warden':
            warden_filter = " AND h.Warden_ID = %s"
            params = (current_user['member_id'], current_user['member_id'], current_user['member_id'])

        # Total Active Residents in their hostel
        cursor.execute(f"""
            SELECT COUNT(*) AS total_residents 
            FROM room_allocations ra
            JOIN rooms r ON ra.Room_ID = r.Room_ID
            JOIN hostels h ON r.Hostel_ID = h.Hostel_ID
            WHERE ra.Status = 'Active' {warden_filter}
        """, params[:1] if warden_filter else ())
        total_residents = cursor.fetchone()['total_residents']

        # Pending Complaints in their hostel
        cursor.execute(f"""
            SELECT COUNT(*) AS pending_complaints 
            FROM complaints c
            JOIN room_allocations ra ON c.Member_ID = ra.Member_ID
            JOIN rooms r ON ra.Room_ID = r.Room_ID
            JOIN hostels h ON r.Hostel_ID = h.Hostel_ID
            WHERE c.Status = 'Pending' AND ra.Status = 'Active' {warden_filter}
        """, params[:1] if warden_filter else ())
        pending_complaints = cursor.fetchone()['pending_complaints']

        # Total Bed Capacity in their hostel
        cursor.execute(f"""
            SELECT SUM(Capacity) AS total_capacity 
            FROM rooms r
            JOIN hostels h ON r.Hostel_ID = h.Hostel_ID
            WHERE 1=1 {warden_filter}
        """, params[:1] if warden_filter else ())
        

        capacity_result = cursor.fetchone()['total_capacity']
        total_capacity = int(capacity_result) if capacity_result else 0
        
    
        available_beds = total_capacity - total_residents

        return jsonify({
            "total_residents": total_residents,
            "pending_complaints": pending_complaints,
            "available_rooms": available_beds
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()



# Warden APIs (Furniture & Movement)
@admin_bp.route('/api/warden/furniture', methods=['GET'])
@token_required
def api_warden_furniture(current_user):
    req_role = current_user['role'].lower()
    if req_role != 'warden':
        return jsonify({"error": "Warden access required."}), 403

    member_id = current_user['member_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT Hostel_ID FROM hostels WHERE Warden_ID = %s", (member_id,))
        hostel = cursor.fetchone()
        if not hostel:
            return jsonify([]), 200

        cursor.execute("""
            SELECT f.Item_Name, COUNT(f.Furniture_ID) as Total_Quantity, SUM(CASE WHEN f.Current_Condition = 'Damaged' THEN 1 ELSE 0 END) as Needs_Repair
            FROM furniture_inventory f JOIN rooms r ON f.Room_ID = r.Room_ID
            WHERE r.Hostel_ID = %s GROUP BY f.Item_Name
        """, (hostel['Hostel_ID'],))
        data = cursor.fetchall()
        
        log_audit(current_user['username'], current_user['role'], f"Warden viewed furniture inventory for Hostel {hostel['Hostel_ID']}")
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@admin_bp.route('/api/warden/movement', methods=['GET'])
@token_required
def api_warden_movement(current_user):
    req_role = current_user['role'].lower()
    if req_role != 'warden':
        return jsonify({"error": "Warden access required."}), 403

    member_id = current_user['member_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT Hostel_ID FROM hostels WHERE Warden_ID = %s", (member_id,))
        hostel = cursor.fetchone()
        if not hostel:
            return jsonify([]), 200

        cursor.execute("""
            SELECT mov.Movement_ID, m.First_Name, m.Last_Name, mov.Exit_Time, mov.Entry_Time, mov.Purpose, r.Room_Number
            FROM member_movement_logs mov JOIN members m ON mov.Member_ID = m.Member_ID
            JOIN room_allocations ra ON m.Member_ID = ra.Member_ID AND ra.Status = 'Active'
            JOIN rooms r ON ra.Room_ID = r.Room_ID
            WHERE r.Hostel_ID = %s ORDER BY mov.Exit_Time DESC
        """, (hostel['Hostel_ID'],))
        data = cursor.fetchall()
        
        log_audit(current_user['username'], current_user['role'], f"Warden viewed movement logs for Hostel {hostel['Hostel_ID']}")
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# Admin APIs (Global Views)
@admin_bp.route('/api/admin/all_furniture', methods=['GET'])
@token_required
def api_admin_all_furniture(current_user):
    if current_user['role'].lower() != 'admin':
        return jsonify({"error": "Admin access required."}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT h.Hostel_Name, f.Item_Name, COUNT(f.Furniture_ID) as Total, SUM(CASE WHEN f.Current_Condition = 'Damaged' THEN 1 ELSE 0 END) as Damaged
            FROM furniture_inventory f JOIN rooms r ON f.Room_ID = r.Room_ID JOIN hostels h ON r.Hostel_ID = h.Hostel_ID
            GROUP BY h.Hostel_Name, f.Item_Name
        """)
        data = cursor.fetchall()
        log_audit(current_user['username'], current_user['role'], "Admin viewed global furniture inventory")
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@admin_bp.route('/api/admin/all_visitors', methods=['GET'])
@token_required
def api_admin_all_visitors(current_user):
    if current_user['role'].lower() != 'admin':
        return jsonify({"error": "Admin access required."}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT h.Hostel_Name, v.Visitor_Name, m.First_Name as Host, v.Entry_Time, v.Exit_Time
            FROM visitor_logs v JOIN members m ON v.Host_Member_ID = m.Member_ID
            JOIN room_allocations ra ON m.Member_ID = ra.Member_ID AND ra.Status = 'Active'
            JOIN rooms r ON ra.Room_ID = r.Room_ID JOIN hostels h ON r.Hostel_ID = h.Hostel_ID
            ORDER BY v.Entry_Time DESC
        """)
        data = cursor.fetchall()
        log_audit(current_user['username'], current_user['role'], "Admin viewed global visitor logs")
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@admin_bp.route('/api/admin/all_movement', methods=['GET'])
@token_required
def api_admin_all_movement(current_user):
    if current_user['role'].lower() != 'admin':
        return jsonify({"error": "Admin access required."}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT h.Hostel_Name, m.First_Name, m.Last_Name, mov.Exit_Time, mov.Entry_Time
            FROM member_movement_logs mov JOIN members m ON mov.Member_ID = m.Member_ID
            JOIN room_allocations ra ON m.Member_ID = ra.Member_ID AND ra.Status = 'Active'
            JOIN rooms r ON ra.Room_ID = r.Room_ID JOIN hostels h ON r.Hostel_ID = h.Hostel_ID
            ORDER BY mov.Exit_Time DESC
        """)
        data = cursor.fetchall()
        log_audit(current_user['username'], current_user['role'], "Admin viewed global student movement logs")
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@admin_bp.route('/api/admin/available-rooms/<int:hostel_id>', methods=['GET'])
@token_required
def get_available_rooms(current_user, hostel_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Select rooms where Capacity > current Active allocations
        query = """
            SELECT r.Room_Number, r.Capacity,
                   (SELECT COUNT(*) FROM room_allocations ra 
                    WHERE ra.Room_ID = r.Room_ID AND ra.Status = 'Active') as Occupied
            FROM rooms r
            WHERE r.Hostel_ID = %s
            HAVING Occupied < Capacity
        """
        cursor.execute(query, (hostel_id,))
        available_rooms = cursor.fetchall()
        
        return jsonify({"rooms": available_rooms}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
