# routes_admin.py
from flask import Blueprint, jsonify
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