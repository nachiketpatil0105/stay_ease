# routes_portfolio.py
from flask import Blueprint, request, jsonify
import mysql.connector
from utils import get_db_connection, token_required, log_audit

portfolio_bp = Blueprint('portfolio_routes', __name__)

@portfolio_bp.route('/portfolio/<int:target_member_id>', methods=['GET', 'PUT'])
@token_required
def manage_portfolio(current_user, target_member_id):
    req_username = current_user['username']
    req_role = current_user['role']
    req_member_id = current_user['member_id']
    
    is_admin = req_role.lower() in ['admin', 'warden']
    
    if not is_admin and req_member_id != target_member_id:
        log_audit(req_username, req_role, f"Attempted to access Member ID {target_member_id}", "UNAUTHORIZED")
        return jsonify({"error": "Access denied. You can only view your own portfolio."}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'GET':
        cursor.execute("""
            SELECT m.First_Name, m.Last_Name, m.Email, m.Contact_Number, 
                   r.Room_Number, h.Hostel_Name
            FROM members m
            LEFT JOIN room_allocations ra ON m.Member_ID = ra.Member_ID AND ra.Status = 'Active'
            LEFT JOIN rooms r ON ra.Room_ID = r.Room_ID
            LEFT JOIN hostels h ON r.Hostel_ID = h.Hostel_ID
            WHERE m.Member_ID = %s
        """, (target_member_id,))
        portfolio = cursor.fetchone()
        
        if not portfolio:
            cursor.close()
            conn.close()
            return jsonify({"error": "Member not found"}), 404

        cursor.execute("""
            SELECT c.Description, c.Submission_Date, c.Status, ct.Type_Name 
            FROM complaints c
            JOIN complaint_types ct ON c.Complaint_Type_ID = ct.Complaint_Type_ID
            WHERE c.Member_ID = %s
            ORDER BY c.Submission_Date DESC
        """, (target_member_id,))
        complaints = cursor.fetchall()

        cursor.execute("""
            SELECT p.Amount_Paid, p.Payment_Date, p.Payment_Status, f.Fee_Name 
            FROM payments p
            JOIN fee_structures f ON p.Fee_Type_ID = f.Fee_Type_ID
            WHERE p.Member_ID = %s
            ORDER BY p.Payment_Date DESC
        """, (target_member_id,))
        payments = cursor.fetchall()

        cursor.close()
        conn.close()
        
        log_audit(req_username, req_role, f"Viewed FULL portfolio of Member ID {target_member_id}")
        return jsonify({
            "profile": portfolio,
            "complaints": complaints,
            "payments": payments
        }), 200

    if request.method == 'PUT':
        update_data = request.get_json()
        new_contact = update_data.get('Contact_Number')
        
        if not new_contact:
            return jsonify({"error": "Missing Contact_Number in payload"}), 400
            
        try:
            cursor.execute("UPDATE members SET Contact_Number = %s WHERE Member_ID = %s", (new_contact, target_member_id))
            conn.commit()
            log_audit(req_username, req_role, f"Updated Contact_Number for Member ID {target_member_id}")
            return jsonify({"message": "Portfolio updated successfully"}), 200
        except mysql.connector.Error as err:
            log_audit(req_username, req_role, f"DB Error updating Member ID {target_member_id}", "FAILED")
            return jsonify({"error": str(err)}), 500
        finally:
            cursor.close()
            conn.close()