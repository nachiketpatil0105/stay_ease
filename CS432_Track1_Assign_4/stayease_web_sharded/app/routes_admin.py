from flask import Blueprint, jsonify, request
import mysql.connector
import datetime

from utils import token_required, log_audit, get_shard_connection, get_all_shard_ports, get_port_connection

admin_bp = Blueprint('admin_routes', __name__)



# VIEW MEMBERS (Scatter-Gather)
@admin_bp.route('/admin/members', methods=['GET'])
@token_required
def get_all_members(current_user):
    req_role = current_user['role'].lower()
    member_id = current_user['member_id'] 
    
    if req_role not in ['admin', 'warden']:
        return jsonify({"error": "Admin access required."}), 403

    all_members = []
    
    # [SHARDING] SCATTER: Ask all 3 databases for their members
    for port in get_all_shard_ports():
        try:
            conn = get_port_connection(port)
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
            if req_role == 'warden':
                query += " AND h.Warden_ID = %s "
                params.append(member_id)
                
            cursor.execute(query, tuple(params))
            all_members.extend(cursor.fetchall()) # GATHER results
        except Exception as e:
            print(f"Error on port {port}: {e}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()
            
    # [SHARDING] Sort the combined list so it looks normal to the frontend
    all_members = sorted(all_members, key=lambda x: x['Member_ID'], reverse=True)
    return jsonify({"members": all_members}), 200


# VIEW COMPLAINTS (Scatter-Gather)
@admin_bp.route('/admin/complaints', methods=['GET'])
@token_required
def get_all_complaints(current_user):
    req_role = current_user['role'].lower()
    member_id = current_user['member_id']

    if req_role not in ['admin', 'warden']:
        return jsonify({"error": "Admin access required."}), 403

    all_complaints = []
    
    # [SHARDING] SCATTER: Ask all 3 databases
    for port in get_all_shard_ports():
        try:
            conn = get_port_connection(port)
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
            if req_role == 'warden':
                query += " WHERE h.Warden_ID = %s "
                params.append(member_id)
                
            cursor.execute(query, tuple(params))
            all_complaints.extend(cursor.fetchall())
        except Exception as e:
            print(f"Error on port {port}: {e}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()
            
    all_complaints = sorted(all_complaints, key=lambda x: x['Submission_Date'] or '', reverse=True)
    return jsonify({"complaints": all_complaints}), 200


# ADD NEW MEMBER (Cross-Shard Logic & Global ID)
@admin_bp.route('/admin/members', methods=['POST'])
@token_required
def add_member(current_user):
    if current_user['role'].lower() not in ['admin', 'warden']:
        return jsonify({"error": "Admin access required."}), 403

    data = request.get_json()
    room_number = data.get('room_number')
    hostel_id = data.get('hostel_id')
    
    room_info = None

    # [SHARDING] 1. Find the Room (It could be on any of the 3 shards)
    for port in get_all_shard_ports():
        conn = get_port_connection(port)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.Room_ID, r.Capacity, 
                   (SELECT COUNT(*) FROM room_allocations ra WHERE ra.Room_ID = r.Room_ID AND ra.Status = 'Active') as Occupied
            FROM rooms r WHERE r.Room_Number = %s AND r.Hostel_ID = %s
        """, (room_number, hostel_id))
        res = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if res:
            room_info = res
            break # Found the room!

    if not room_info:
        return jsonify({"error": f"Room {room_number} does not exist in Hostel {hostel_id}."}), 404
    if room_info['Occupied'] >= room_info['Capacity']:
        return jsonify({"error": f"Room {room_number} is full."}), 400

    # [SHARDING] 2. Generate Global Member_ID (Find max ID across all shards + 1)
    max_id = 0
    for port in get_all_shard_ports():
        conn = get_port_connection(port)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(Member_ID) FROM members")
        res = cursor.fetchone()[0]
        if res and res > max_id:
            max_id = res
        cursor.close()
        conn.close()
        
    new_member_id = max_id + 1

    # [SHARDING] 3. Route insert to the EXACT shard using Member_ID % 3
    target_conn = get_shard_connection(new_member_id)
    target_cursor = target_conn.cursor()

    try:
        target_conn.start_transaction() 

        # Insert Member with Explicit ID
        member_query = """
            INSERT INTO members 
            (Member_ID, First_Name, Last_Name, Gender, Age, Contact_Number, Email, Emergency_Contact, Image_Path, Role_ID, Status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        member_values = (
            new_member_id, data.get('first_name'), data.get('last_name', ''), data.get('gender'), 
            data.get('age'), data.get('contact'), data.get('email'), data.get('emergency_contact', ''), 
            data.get('image_path', 'uploads/default.png'), data.get('role_id'), 'Active'
        )
        target_cursor.execute(member_query, member_values)
        
        # Insert Allocation
        allocation_query = """
            INSERT INTO room_allocations (Member_ID, Room_ID, Allocation_Date, Status)
            VALUES (%s, %s, %s, %s)
        """
        target_cursor.execute(allocation_query, (new_member_id, room_info['Room_ID'], datetime.date.today(), 'Active'))

        target_conn.commit()
        log_audit(current_user['username'], current_user['role'], f"Added member {new_member_id} to room {room_info['Room_ID']}")

        target_port = 3307 + (new_member_id % 3)
        print(f"SUCCESS: Routed new Member ID {new_member_id} to Shard Port {target_port}!")

        return jsonify({"message": "Member added and room allocated successfully!"}), 201

    except Exception as e:
        target_conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        target_cursor.close()
        target_conn.close()


# UPDATE MEMBER (Specific Shard Target)
@admin_bp.route('/admin/members/<int:member_id>', methods=['PUT'])
@token_required
def update_member(current_user, member_id):
    if current_user['role'].lower() not in ['admin', 'warden']:
        return jsonify({"error": "Admin access required."}), 403

    data = request.get_json()
    
    # [SHARDING] We know the Member_ID, so we target ONLY that specific port!
    conn = get_shard_connection(member_id)
    cursor = conn.cursor()

    try:
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


# UPDATE COMPLAINT (Broadcast Update)
@admin_bp.route('/admin/complaints/<int:complaint_id>', methods=['PUT'])
@token_required
def update_complaint_status(current_user, complaint_id):
    if current_user['role'].lower() not in ['admin', 'warden']:
        return jsonify({"error": "Admin access required."}), 403

    data = request.get_json()
    new_status = data.get('status')
    
    # [SHARDING] Broadcast update to all shards. 2 will affect 0 rows, 1 will succeed.
    for port in get_all_shard_ports():
        try:
            conn = get_port_connection(port)
            cursor = conn.cursor()
            if new_status == 'Resolved':
                query = "UPDATE complaints SET Status = %s, Resolved_Date = CURRENT_DATE() WHERE Complaint_ID = %s"
            else:
                query = "UPDATE complaints SET Status = %s, Resolved_Date = NULL WHERE Complaint_ID = %s"
                
            cursor.execute(query, (new_status, complaint_id))
            conn.commit()
        except Exception as e:
            print(f"Error updating complaint on port {port}: {e}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    log_audit(current_user['username'], current_user['role'], f"Updated Complaint {complaint_id} to {new_status}")
    return jsonify({"message": "Complaint status updated!"}), 200



# DELETE COMPLAINT (Broadcast Delete)
@admin_bp.route('/admin/complaints/<int:complaint_id>', methods=['DELETE'])
@token_required
def delete_complaint(current_user, complaint_id):
    if current_user['role'].lower() not in ['admin', 'warden']:
        return jsonify({"error": "Admin access required."}), 403

    # [SHARDING] Broadcast delete to all shards
    for port in get_all_shard_ports():
        try:
            conn = get_port_connection(port)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM complaints WHERE Complaint_ID = %s", (complaint_id,))
            conn.commit()
        except Exception as e:
            pass
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    return jsonify({"message": "Complaint deleted successfully!"}), 200


# ADMIN STATS (Scatter-Gather Sums)
@admin_bp.route('/admin/stats', methods=['GET'])
@token_required
def get_admin_stats(current_user):
    if current_user['role'].lower() not in ['admin', 'warden']:
        return jsonify({"error": "Unauthorized"}), 403

    total_residents = 0
    pending_complaints = 0
    total_capacity = 0

    warden_filter = ""
    params = ()
    if current_user['role'].lower() == 'warden':
        warden_filter = " AND h.Warden_ID = %s"
        params = (current_user['member_id'], current_user['member_id'], current_user['member_id'])

    # [SHARDING] 1. Get Capacity from ONLY ONE shard (since rooms are replicated everywhere)
    try:
        conn = get_port_connection(3307) # Just ask Shard 1
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT SUM(Capacity) AS c FROM rooms r JOIN hostels h ON r.Hostel_ID = h.Hostel_ID WHERE 1=1 {warden_filter}", params[:1] if warden_filter else ())
        res = cursor.fetchone()['c']
        if res: total_capacity = int(res)
    except Exception as e:
        print(f"Capacity Error: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

    # [SHARDING] 2. Scatter-Gather residents and complaints across ALL shards
    for port in get_all_shard_ports():
        try:
            conn = get_port_connection(port)
            cursor = conn.cursor(dictionary=True)
            
            # Residents
            cursor.execute(f"SELECT COUNT(*) AS c FROM room_allocations ra JOIN rooms r ON ra.Room_ID = r.Room_ID JOIN hostels h ON r.Hostel_ID = h.Hostel_ID WHERE ra.Status = 'Active' {warden_filter}", params[:1] if warden_filter else ())
            total_residents += cursor.fetchone()['c']

            # Complaints
            cursor.execute(f"SELECT COUNT(*) AS c FROM complaints c JOIN room_allocations ra ON c.Member_ID = ra.Member_ID JOIN rooms r ON ra.Room_ID = r.Room_ID JOIN hostels h ON r.Hostel_ID = h.Hostel_ID WHERE c.Status = 'Pending' AND ra.Status = 'Active' {warden_filter}", params[:1] if warden_filter else ())
            pending_complaints += cursor.fetchone()['c']

        except Exception as e:
            print(f"Stats Error on port {port}: {e}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    return jsonify({
        "total_residents": total_residents,
        "pending_complaints": pending_complaints,
        "available_rooms": total_capacity - total_residents
    }), 200



# GLOBAL APIs (Scatter Gather)
@admin_bp.route('/api/admin/available-rooms/<int:hostel_id>', methods=['GET'])
@token_required
def get_admin_available_rooms(current_user, hostel_id):
    available_rooms = []
    
    for port in get_all_shard_ports():
        try:
            conn = get_port_connection(port)
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT r.Room_Number, r.Capacity,
                       (SELECT COUNT(*) FROM room_allocations ra WHERE ra.Room_ID = r.Room_ID AND ra.Status = 'Active') as Occupied
                FROM rooms r
                WHERE r.Hostel_ID = %s
                HAVING Occupied < Capacity
            """
            cursor.execute(query, (hostel_id,))
            available_rooms.extend(cursor.fetchall())
        except Exception as e:
            pass
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()
            
    return jsonify({"rooms": available_rooms}), 200



@admin_bp.route('/api/warden/available-rooms/<int:hostel_id>', methods=['GET'])
@token_required
def get_warden_available_rooms(current_user, hostel_id):
    available_rooms = []
    
    for port in get_all_shard_ports():
        try:
            conn = get_port_connection(port)
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT r.Room_Number, r.Capacity,
                       (SELECT COUNT(*) FROM room_allocations ra WHERE ra.Room_ID = r.Room_ID AND ra.Status = 'Active') as Occupied
                FROM rooms r
                WHERE r.Hostel_ID = %s
                HAVING Occupied < Capacity
            """
            cursor.execute(query, (hostel_id,))
            available_rooms.extend(cursor.fetchall())
        except Exception as e:
            pass
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()
            
    return jsonify({"rooms": available_rooms}), 200

