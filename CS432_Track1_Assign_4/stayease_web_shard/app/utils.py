import mysql.connector
import jwt
import logging
import os
from functools import wraps
from flask import request, jsonify

SECRET_KEY = 'stayease_super_secret_key_2026'

# Logger Setup
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


# Shard Connection
REMOTE_HOST = "10.0.116.184"
DB_USER = "QueryCraft"
DB_PASS = "password@123"
DB_NAME = "QueryCraft"

def get_shard_connection(member_id):
    """
    Routes to a specific shard based on the Member_ID.
    Used for lookups and inserts for a specific user.
    """
    shard_index = int(member_id) % 3
    port_mapping = {
        0: 3307, # Shard 1
        1: 3308, # Shard 2
        2: 3309  # Shard 3
    }
    
    return mysql.connector.connect(
        host=REMOTE_HOST,
        port=port_mapping[shard_index],
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )

def get_all_shard_ports():
    """Returns the list of all shard ports for range queries."""
    return [3307, 3308, 3309]


# Security Token Decorator 
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


#Get connection to a specific port
def get_port_connection(port):
    return mysql.connector.connect(
        host=REMOTE_HOST, port=port, 
        user=DB_USER, password=DB_PASS, database=DB_NAME
    )
