from flask import Blueprint, jsonify, request
from utils import get_shard_connection, token_required, log_audit

security_bp = Blueprint('security_bp', __name__)

# Security Dashboard (Scatter-Gather Query)
@security_bp.route('/api/security/dashboard', methods=['GET'])
@token_required
def api_security_dashboard(current_user):
    if current_user['role'].lower() != 'security':
        return jsonify({"error": "Security access required."}), 403

    guard_id = current_user['member_id']
    
    # Step 1: Get the Guard's Hostel from Shard 1 (Since Hostels are replicated everywhere)
    conn_primary = get_shard_connection(0)
    cursor_primary = conn_primary.cursor(dictionary=True)
    try:
        cursor_primary.execute("SELECT Hostel_ID, Hostel_Name FROM hostels WHERE Security_ID = %s", (guard_id,))
        hostel = cursor_primary.fetchone()
    finally:
        cursor_primary.close()
        conn_primary.close()

    if not hostel:
        return jsonify({"active_visitors": [], "outside_students": [], "hostel_name": "Unassigned"}), 200

    hostel_id = hostel['Hostel_ID']
    all_active_visitors = []
    all_outside_students = []

    # Step 2: SCATTER-GATHER - Ask all 3 shards for students belonging to this hostel
    # We pass 0, 1, 2 into get_shard_connection to force connections to Port 3307, 3308, 3309
    for shard_id in [0, 1, 2]:
        try:
            conn = get_shard_connection(shard_id)
            cursor = conn.cursor(dictionary=True)

            # Fetch Inside Visitors
            cursor.execute("""
                SELECT v.Log_ID, v.Visitor_Name, v.Purpose, m.First_Name as Visiting_Student, r.Room_Number, v.Entry_Time
                FROM visitor_logs v
                JOIN members m ON v.Host_Member_ID = m.Member_ID
                JOIN room_allocations ra ON m.Member_ID = ra.Member_ID AND ra.Status = 'Active'
                JOIN rooms r ON ra.Room_ID = r.Room_ID
                WHERE r.Hostel_ID = %s AND v.Exit_Time IS NULL
            """, (hostel_id,))
            all_active_visitors.extend(cursor.fetchall())

            # Fetch Outside Students
            cursor.execute("""
                SELECT mov.Movement_ID, m.First_Name, m.Last_Name, m.Contact_Number, mov.Exit_Time, mov.Purpose
                FROM member_movement_logs mov
                JOIN members m ON mov.Member_ID = m.Member_ID
                JOIN room_allocations ra ON m.Member_ID = ra.Member_ID AND ra.Status = 'Active'
                JOIN rooms r ON ra.Room_ID = r.Room_ID
                WHERE r.Hostel_ID = %s AND mov.Entry_Time IS NULL
            """, (hostel_id,))
            all_outside_students.extend(cursor.fetchall())

        except Exception as e:
            print(f"Dashboard Error on Shard {shard_id}: {e}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    log_audit(current_user['username'], current_user['role'], f"Security Guard viewed dashboard for Hostel {hostel_id}")

    return jsonify({
        "hostel_name": hostel['Hostel_Name'],
        "active_visitors": all_active_visitors,
        "outside_students": all_outside_students
    }), 200


# Add New Visitor (Direct Routing)
@security_bp.route('/api/security/visitors', methods=['POST'])
@token_required
def add_new_visitor(current_user):
    if current_user['role'].lower() not in ['security', 'admin']:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    host_id = data.get('host_id')
    
    # DIRECT ROUTING: We know the Host's Member ID, so route directly to their specific shard!
    conn = get_shard_connection(host_id)
    cursor = conn.cursor()

    try:
        query = """
            INSERT INTO visitor_logs 
            (Visitor_Name, Contact_Number, ID_Proof_Type, ID_Proof_Number, Host_Member_ID, Entry_Time, Purpose)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s)
        """
        values = (
            data.get('visitor_name'), data.get('contact'), data.get('id_type'),
            data.get('id_number'), host_id, data.get('purpose')
        )
        cursor.execute(query, values)
        conn.commit()
        return jsonify({"message": "Visitor successfully logged!"}), 201
    except Exception as e:
        conn.rollback()
        if 'foreign key constraint fails' in str(e).lower():
             return jsonify({"error": "Invalid Host Student ID. Student not found."}), 400
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# Visitors Sign Out (Broadcast Routing)
@security_bp.route('/api/security/visitors/<int:log_id>/exit', methods=['PUT'])
@token_required
def mark_visitor_exited(current_user, log_id):
    if current_user['role'].lower() not in ['security', 'admin']:
        return jsonify({"error": "Unauthorized"}), 403

    # BROADCAST ROUTING: We only have Log_ID, not the Student ID. 
    # Try updating all 3 shards until one says "I updated a row!"
    for shard_id in [0, 1, 2]:
        try:
            conn = get_shard_connection(shard_id)
            cursor = conn.cursor()
            
            query = "UPDATE visitor_logs SET Exit_Time = NOW() WHERE Log_ID = %s AND Exit_Time IS NULL"
            cursor.execute(query, (log_id,))
            conn.commit()

            if cursor.rowcount > 0:
                # We found the record and updated it! Stop searching.
                return jsonify({"message": "Visitor successfully signed out!"}), 200

        except Exception as e:
            conn.rollback()
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    return jsonify({"error": "Visitor already signed out or Log ID not found."}), 400


# Student Sign-In (Broadcast Routing)
@security_bp.route('/api/movement/<int:log_id>/return', methods=['PUT'])
@token_required
def mark_student_returned(current_user, log_id):
    if current_user['role'].lower() not in ['security', 'warden', 'admin']:
        return jsonify({"error": "Unauthorized"}), 403

    # BROADCAST ROUTING: Send to all 3 shards until the log is found
    for shard_id in [0, 1, 2]:
        try:
            conn = get_shard_connection(shard_id)
            cursor = conn.cursor()
            
            query = "UPDATE member_movement_logs SET Entry_Time = NOW() WHERE Log_ID = %s AND Entry_Time IS NULL"
            cursor.execute(query, (log_id,))
            conn.commit()

            if cursor.rowcount > 0:
                return jsonify({"message": "Student successfully marked as returned!"}), 200

        except Exception as e:
            conn.rollback()
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    return jsonify({"error": "Student already marked as returned or Log ID not found."}), 400


# Finding Host for Adding Visitor (Scatter-Gather Search)
@security_bp.route('/api/security/search-student', methods=['GET'])
@token_required
def search_student(current_user):
    if current_user['role'].lower() not in ['security', 'admin']:
        return jsonify({"error": "Unauthorized"}), 403

    search_query = request.args.get('q', '')
    if len(search_query) < 2:
        return jsonify([]), 200

    # Step 1: Find the hostel this security guard belongs to (from Shard 1)
    conn_primary = get_shard_connection(0)
    cursor_primary = conn_primary.cursor(dictionary=True)
    try:
        cursor_primary.execute("SELECT Hostel_ID FROM hostels WHERE Security_ID = %s", (current_user['member_id'],))
        hostel = cursor_primary.fetchone()
    finally:
        cursor_primary.close()
        conn_primary.close()

    if not hostel:
        return jsonify([]), 200
    hostel_id = hostel['Hostel_ID']

    all_results = []
    like_q = f"%{search_query}%"

    # Step 2: SCATTER-GATHER - Search all 3 shards for students matching the text
    for shard_id in [0, 1, 2]:
        try:
            conn = get_shard_connection(shard_id)
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT m.Member_ID, m.First_Name, m.Last_Name, m.Contact_Number, r.Room_Number
                FROM members m
                JOIN room_allocations ra ON m.Member_ID = ra.Member_ID AND ra.Status = 'Active'
                JOIN rooms r ON ra.Room_ID = r.Room_ID
                WHERE r.Hostel_ID = %s AND m.Status = 'Active'
                AND (m.First_Name LIKE %s OR m.Last_Name LIKE %s OR r.Room_Number LIKE %s OR m.Contact_Number LIKE %s)
                LIMIT 10
            """
            cursor.execute(query, (hostel_id, like_q, like_q, like_q, like_q))
            all_results.extend(cursor.fetchall())
        except Exception as e:
            pass
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    # Limit total merged results to 10
    return jsonify(all_results[:10]), 200