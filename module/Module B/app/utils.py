# utils.py
import mysql.connector
import jwt
import logging
import os
from functools import wraps
from flask import request, jsonify

SECRET_KEY = 'stayease_super_secret_key_2026'

# --- Logger Setup ---
LOG_DIR = '../logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

logging.basicConfig(
    filename=f'{LOG_DIR}/audit.log',
    level=logging.INFO,
    format='[%(asctime)s] - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    force=True
)

def log_audit(username, role, action, status="SUCCESS"):
    message = f"User: '{username}' (Role: {role}) | Action: {action} | Status: {status}"
    if status == "SUCCESS":
        logging.info(message)
    else:
        logging.warning(message)

# --- Database Connection ---
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Niraj@1607',  # Ensure this matches your MySQL password!
        database='stayease'
    )

# --- Security Token Decorator ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
            
        if not token:
            return jsonify({"error": "Authentication token is missing!"}), 401
            
        try:
            current_user = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Session expired, please log in again."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token."}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated