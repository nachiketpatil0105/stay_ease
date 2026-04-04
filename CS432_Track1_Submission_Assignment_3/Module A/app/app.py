import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify, render_template

# Importing custom database engine
from db_engine.db_manager import DatabaseManager
from db_engine.transaction_manager import TransactionManager

app = Flask(__name__)


# Initializing Custom B+ Tree Engine
print("\nBooting up StayEase Custom B+ Tree Engine!!")
db = DatabaseManager()
db.create_database("stayease")

# Create the 3 Required Tables for Assignment 3
db.create_table("stayease", "members", {"Member_ID": int, "First_Name": str, "Last_Name": str, "Fee_Balance": float}, search_key="Member_ID")
db.create_table("stayease", "rooms", {"Room_Number": str, "Available_Beds": int}, search_key="Room_Number")
db.create_table("stayease", "allocations", {"Alloc_ID": int, "Member_ID": int, "Room_Number": str}, search_key="Alloc_ID")

# Insert Initial Mock Data so that website form has a room to actually book
rooms = db.get_table("stayease", "rooms")[0]
rooms.insert({"Room_Number": "101", "Available_Beds": 2})
rooms.insert({"Room_Number": "102", "Available_Beds": 3})

# Boot up the Transaction Manager & Run Crash Recovery
tx_manager = TransactionManager(db, log_file="stayease_wal.log")
tx_manager.recover()
print("Database Engine Ready!\n")


# Importing custom blueprints (Moved down here to prevent circular imports)
from routes_auth import auth_bp
from routes_portfolio import portfolio_bp
from routes_admin import admin_bp
from routes_security import security_bp

# Register the routes with the main app
app.register_blueprint(auth_bp)
app.register_blueprint(portfolio_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(security_bp)


# Frontend & Base Routes
@app.route('/', methods=['GET'])
def welcome():
    return jsonify({"message": "Welcome to test APIs"}), 200

@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)