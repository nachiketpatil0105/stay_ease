# routes_admin.py
from flask import Blueprint, jsonify, request
from utils import get_db_connection, token_required, log_audit

admin_bp = Blueprint('admin_routes', __name__)

@admin_bp.route('/admin/members', methods=['GET'])
@token_required
def get_all_members(current_user):
    req_username = current_user['username']
    req_role = current_user['role']
    
    if req_role.lower() not in ['admin', 'warden']:
        log_audit(req_username, req_role, "Attempted to view all members list", "UNAUTHORIZED")
        return jsonify({"error": "Admin access required. Action logged."}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT Member_ID, First_Name, Last_Name, Email, Contact_Number, Status FROM members")
    all_members = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    log_audit(req_username, req_role, "Successfully viewed all members list")
    return jsonify({"members": all_members}), 200

@admin_bp.route('/admin/member', methods=['POST'])
@token_required
def create_member(current_user):
    if current_user['role'].lower() not in ['admin', 'warden']:
        return jsonify({"error": "Only admin can add members"}), 403

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    required_fields = [
        'First_Name', 'Gender', 'Age',
        'Contact_Number', 'Email', 'Role_ID', 'Status'
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO members 
            (First_Name, Last_Name, Gender, Age, Contact_Number, Email, Role_ID, Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['First_Name'],
            data['Last_Name'],
            data['Gender'],
            data['Age'],
            data['Contact_Number'],
            data['Email'],
            data['Role_ID'],
            data['Status']
        ))

        conn.commit()

        log_audit(
        current_user['username'],
        current_user['role'],
        f"Created new member with email {data['Email']}"
    )

        return jsonify({"message": "Member created successfully"}), 201

    except Exception as e:
        log_audit(current_user['username'], current_user['role'], f"Failed to create member: {str(e)}", "FAILED")
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()