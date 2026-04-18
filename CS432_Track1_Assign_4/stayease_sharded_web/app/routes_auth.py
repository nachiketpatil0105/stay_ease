from flask import Blueprint, request, jsonify
import jwt
import datetime
from werkzeug.security import check_password_hash
from utils import get_shard_connection, SECRET_KEY, log_audit

auth_bp = Blueprint('auth_routes', __name__)

@auth_bp.route('/login', methods=['POST']) # Make sure this URL matches your frontend fetch URL!
def login():
    # Check if it's JSON or a standard HTML Form
    if request.is_json:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
    else:
        username = request.form.get('username')
        password = request.form.get('password')

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    # STEP 1: Ask Shard 1 for credentials (since user_credentials is replicated)
    try:
        conn_auth = get_shard_connection(0)
        cursor_auth = conn_auth.cursor(dictionary=True)
        cursor_auth.execute("SELECT Member_ID, Password_Hash FROM user_credentials WHERE Username = %s", (username,))
        user_cred = cursor_auth.fetchone()
    finally:
        if 'cursor_auth' in locals(): cursor_auth.close()
        if 'conn_auth' in locals(): conn_auth.close()

    # Check if user exists and password is correct
    if not user_cred or not check_password_hash(user_cred['Password_Hash'], password):
        log_audit(username, "UNKNOWN", "Failed login attempt", "FAILED")
        return jsonify({"error": "Invalid credentials"}), 401

    member_id = user_cred['Member_ID']

    # STEP 2: Now route DIRECTLY to the correct shard to get their Profile & Role!
    try:
        # This will automatically calculate Member_ID % 3 and go to the right port
        conn_profile = get_shard_connection(member_id)
        cursor_profile = conn_profile.cursor(dictionary=True)
        cursor_profile.execute("""
            SELECT m.First_Name, m.Last_Name, r.Role_Name 
            FROM members m
            JOIN roles r ON m.Role_ID = r.Role_ID
            WHERE m.Member_ID = %s
        """, (member_id,))
        user_profile = cursor_profile.fetchone()
    finally:
        if 'cursor_profile' in locals(): cursor_profile.close()
        if 'conn_profile' in locals(): conn_profile.close()

    if not user_profile:
        return jsonify({"error": "Profile data missing on shard"}), 500

    # Generate JWT Token
    token = jwt.encode({
        'member_id': member_id,
        'username': username,
        'role': user_profile['Role_Name'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, SECRET_KEY, algorithm='HS256')

    log_audit(username, user_profile['Role_Name'], "User logged in successfully")

    return jsonify({
        "message": "Login successful",
        "token": token,
        "role": user_profile['Role_Name'],
        "name": user_profile['First_Name']
    }), 200


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