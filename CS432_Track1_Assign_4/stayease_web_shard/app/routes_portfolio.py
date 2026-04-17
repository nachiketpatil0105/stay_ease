from flask import Blueprint, request, jsonify
import mysql.connector
from utils import get_shard_connection, token_required, log_audit
import datetime

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

    # [SHARDING FIX] Route directly to the specific shard holding this member's data!
    conn = get_shard_connection(target_member_id)
    cursor = conn.cursor(dictionary=True)

    if request.method == 'GET':
        cursor.execute("""
            SELECT 
                m.First_Name, m.Last_Name, m.Email, m.Contact_Number, m.Image_Path,
                r.Room_Number,
                COALESCE(h_student.Hostel_ID, h_warden.Hostel_ID, h_security.Hostel_ID) AS Hostel_ID,
                COALESCE(h_student.Hostel_Name, h_warden.Hostel_Name, h_security.Hostel_Name) AS Hostel_Name
            FROM members m
            
            -- Path 1: For Students (Looks for their room)
            LEFT JOIN room_allocations ra ON m.Member_ID = ra.Member_ID AND ra.Status = 'Active'
            LEFT JOIN rooms r ON ra.Room_ID = r.Room_ID
            LEFT JOIN hostels h_student ON r.Hostel_ID = h_student.Hostel_ID
            
            -- Path 2: For Wardens (Looks for the hostel they manage)
            LEFT JOIN hostels h_warden ON m.Member_ID = h_warden.Warden_ID
            
            -- Path 3: For Security Guards (Looks for the hostel they guard)
            LEFT JOIN hostels h_security ON m.Member_ID = h_security.Security_ID
            
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

        # NOTE: If you get a 'payments table does not exist' error later, 
        # it means you need to add the payments table to your shard/replicate script!
        try:
            cursor.execute("""
                SELECT p.Amount_Paid, p.Payment_Date, p.Payment_Status, f.Fee_Name 
                FROM payments p
                JOIN fee_structures f ON p.Fee_Type_ID = f.Fee_Type_ID
                WHERE p.Member_ID = %s
                ORDER BY p.Payment_Date DESC
            """, (target_member_id,))
            payments = cursor.fetchall()
        except mysql.connector.Error:
            payments = [] # Failsafe if payments table isn't migrated yet

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



# Raise a New Complaint (Student Only)
@portfolio_bp.route('/portfolio/complaints', methods=['POST'])
@token_required
def raise_complaint(current_user):
    if current_user['role'].lower() != 'student':
        return jsonify({"error": "Only students can raise complaints here."}), 403

    data = request.get_json()
    member_id = current_user['member_id'] # Secured from the JWT token
    
    # [SHARDING FIX] Route directly to the shard holding this student!
    conn = get_shard_connection(member_id)
    cursor = conn.cursor()

    try:
        query = """
            INSERT INTO complaints (Member_ID, Complaint_Type_ID, Description, Submission_Date, Status)
            VALUES (%s, %s, %s, %s, 'Pending')
        """
        current_date = datetime.date.today()
        cursor.execute(query, (member_id, data['type_id'], data['description'], current_date))
        conn.commit()
        
        log_audit(current_user['username'], current_user['role'], f"Raised a new complaint.")
        
        # ADDING A PRINT STATEMENT FOR YOUR VIDEO DEMO!
        target_port = 3307 + (member_id % 3)
        print(f"SUCCESS: Routed new complaint for Member {member_id} directly to Shard Port {target_port}!")
        
        return jsonify({"message": "Complaint submitted successfully!"}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()