# ADDED 'request' to the import list here:
from flask import Blueprint, jsonify, request
from utils import get_db_connection, token_required, log_audit

security_bp = Blueprint('security_bp', __name__)

@security_bp.route('/api/security/dashboard', methods=['GET'])
@token_required
def api_security_dashboard(current_user):
    # 1. Check Role
    if current_user['role'].lower() != 'security':
        return jsonify({"error": "Security access required."}), 403

    guard_id = current_user['member_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 2. Find Guard's Hostel
        cursor.execute("SELECT Hostel_ID, Hostel_Name FROM hostels WHERE Security_ID = %s", (guard_id,))
        hostel = cursor.fetchone()

        if not hostel:
            return jsonify({"active_visitors": [], "outside_students": [], "hostel_name": "Unassigned"}), 200

        hostel_id = hostel['Hostel_ID']

        # 3. Fetch Inside Visitors
        cursor.execute("""
            SELECT v.Log_ID, v.Visitor_Name, v.Purpose, m.First_Name as Visiting_Student, r.Room_Number, v.Entry_Time
            FROM visitor_logs v
            JOIN members m ON v.Host_Member_ID = m.Member_ID
            JOIN room_allocations ra ON m.Member_ID = ra.Member_ID AND ra.Status = 'Active'
            JOIN rooms r ON ra.Room_ID = r.Room_ID
            WHERE r.Hostel_ID = %s AND v.Exit_Time IS NULL
        """, (hostel_id,))
        active_visitors = cursor.fetchall()

        # 4. Fetch Outside Students
        cursor.execute("""
            SELECT mov.Movement_ID, m.First_Name, m.Last_Name, m.Contact_Number, mov.Exit_Time, mov.Purpose
            FROM member_movement_logs mov
            JOIN members m ON mov.Member_ID = m.Member_ID
            JOIN room_allocations ra ON m.Member_ID = ra.Member_ID AND ra.Status = 'Active'
            JOIN rooms r ON ra.Room_ID = r.Room_ID
            WHERE r.Hostel_ID = %s AND mov.Entry_Time IS NULL
        """, (hostel_id,))
        outside_students = cursor.fetchall()

        # 5. Log the action using your custom audit logger
        log_audit(current_user['username'], current_user['role'], f"Security Guard viewed dashboard for Hostel {hostel_id}")

        return jsonify({
            "hostel_name": hostel['Hostel_Name'],
            "active_visitors": active_visitors,
            "outside_students": outside_students
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# CHANGED @app.route to @security_bp.route here:
@security_bp.route('/api/security/visitors', methods=['POST'])
@token_required
def add_new_visitor(current_user):
    # Ensure only security guards (or admins) can add visitors
    if current_user['role'].lower() not in ['security', 'admin']:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # We use NOW() for Entry_Time, and Exit_Time remains NULL until they leave
        query = """
            INSERT INTO visitor_logs 
            (Visitor_Name, Contact_Number, ID_Proof_Type, ID_Proof_Number, Host_Member_ID, Entry_Time, Purpose)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s)
        """
        values = (
            data.get('visitor_name'),
            data.get('contact'),
            data.get('id_type'),
            data.get('id_number'),
            data.get('host_id'),
            data.get('purpose')
        )
        
        cursor.execute(query, values)
        conn.commit()
        
        return jsonify({"message": "Visitor successfully logged!"}), 201

    except Exception as e:
        conn.rollback()
        # If the host_id doesn't exist in the members table, it will trigger a foreign key error
        if 'foreign key constraint fails' in str(e).lower():
             return jsonify({"error": "Invalid Host Student ID. Student not found."}), 400
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@security_bp.route('/api/security/visitors/<int:log_id>/exit', methods=['PUT'])
@token_required
def mark_visitor_exited(current_user, log_id):
    # Only security guards and admins can sign visitors out
    if current_user['role'].lower() not in ['security', 'admin']:
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Update the Exit_Time to the exact current timestamp
        query = """
            UPDATE visitor_logs 
            SET Exit_Time = NOW() 
            WHERE Log_ID = %s AND Exit_Time IS NULL
        """
        cursor.execute(query, (log_id,))
        conn.commit()

        # Check if the row was actually updated (prevents double-clicking issues)
        if cursor.rowcount == 0:
            return jsonify({"error": "Visitor already signed out or Log ID not found."}), 400

        return jsonify({"message": "Visitor successfully signed out!"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@security_bp.route('/api/movement/<int:log_id>/return', methods=['PUT'])
@token_required
def mark_student_returned(current_user, log_id):
    # Allow Security, Wardens, and Admins to mark a student as returned
    if current_user['role'].lower() not in ['security', 'warden', 'admin']:
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Update the Entry_Time to the current timestamp
        query = """
            UPDATE member_movement_logs 
            SET Entry_Time = NOW() 
            WHERE Log_ID = %s AND Entry_Time IS NULL
        """
        cursor.execute(query, (log_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Student already marked as returned or Log ID not found."}), 400

        return jsonify({"message": "Student successfully marked as returned!"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@security_bp.route('/api/security/search-student', methods=['GET'])
@token_required
def search_student(current_user):
    # Ensure they are authorized
    if current_user['role'].lower() not in ['security', 'admin']:
        return jsonify({"error": "Unauthorized"}), 403

    search_query = request.args.get('q', '')
    if len(search_query) < 2:
        return jsonify([]), 200

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # First, find the hostel this security guard belongs to
        cursor.execute("SELECT Hostel_ID FROM hostels WHERE Security_ID = %s", (current_user['member_id'],))
        hostel = cursor.fetchone()
        
        if not hostel:
            return jsonify([]), 200
            
        hostel_id = hostel['Hostel_ID']

        # Secure query using LIKE operator for Name, Room, or Phone
        query = """
            SELECT m.Member_ID, m.First_Name, m.Last_Name, m.Contact_Number, r.Room_Number
            FROM members m
            JOIN room_allocations ra ON m.Member_ID = ra.Member_ID AND ra.Status = 'Active'
            JOIN rooms r ON ra.Room_ID = r.Room_ID
            WHERE r.Hostel_ID = %s 
            AND m.Status = 'Active'
            AND (m.First_Name LIKE %s OR m.Last_Name LIKE %s OR r.Room_Number LIKE %s OR m.Contact_Number LIKE %s)
            LIMIT 10
        """
        
        # Add wildcards to the search term
        like_q = f"%{search_query}%"
        
        # Execute with parameters
        cursor.execute(query, (hostel_id, like_q, like_q, like_q, like_q))
        results = cursor.fetchall()
        
        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()