from app import app
from flask import jsonify, render_template

@app.route('/', methods=['GET'])
def root():
    return jsonify({"message": "Welcome to test APIs"})

@app.route('/login', methods=['POST'])
def login():
    return jsonify({
        "message": "Login successful",
        "session_token": "dummy_jwt_token_for_now"
    })

@app.route('/isAuth', methods=['GET'])
def isAuth():
    return jsonify({
        "message": "User is authenticated", 
        "username": "test_student", 
        "role": "Regular User", 
        "expiry": "2026-03-15"
    })

@app.route('/portfolio', methods = ['Get'])
def portfolio():
    user = {'username': 'User_name'}
    return render_template('pf.html', title = 'Portfolio', user = user)