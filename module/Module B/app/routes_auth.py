# routes_auth.py
from flask import Blueprint, request, jsonify
import jwt
import datetime
from werkzeug.security import check_password_hash
from utils import get_db_connection, SECRET_KEY, log_audit

auth_bp = Blueprint('auth_routes', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('user') or not data.get('password'):
        return jsonify({"error": "Missing parameters"}), 401

    username = data.get('user')
    password_attempt = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT uc.Password_Hash, m.Member_ID, r.Role_Name
        FROM user_credentials uc
        JOIN members m ON uc.Member_ID = m.Member_ID
        JOIN roles r ON m.Role_ID = r.Role_ID
        WHERE uc.Username = %s
    """
    cursor.execute(query, (username,))
    user_record = cursor.fetchone()
    cursor.close()
    conn.close()

    if user_record and check_password_hash(user_record['Password_Hash'].strip(), password_attempt):
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        token_payload = {
            'username': username,
            'member_id': user_record['Member_ID'],
            'role': user_record['Role_Name'],
            'exp': expiration_time
        }
        token = jwt.encode(token_payload, SECRET_KEY, algorithm='HS256')
        
        log_audit(username, user_record['Role_Name'], "User logged in successfully")
        return jsonify({
            "message": "Login successful",
            "session token": token
        }), 200
        
    log_audit(username, "Unknown", "Failed login attempt", "FAILED")
    return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route('/isAuth', methods=['GET'])
def is_auth():
    token = None
    if 'Authorization' in request.headers:
        token = request.headers['Authorization'].split(" ")[1]
    elif request.is_json and 'session token' in request.get_json():
        token = request.get_json()['session token']

    if not token:
        return jsonify({"error": "No session found"}), 401

    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        expiry_datetime = datetime.datetime.utcfromtimestamp(decoded_data['exp'])
        return jsonify({
            "message": "User is authenticated",
            "username": decoded_data['username'],
            "role": decoded_data['role'],
            "expiry": expiry_datetime.strftime('%Y-%m-%d %H:%M:%S')
        }), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Session expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid session token"}), 401