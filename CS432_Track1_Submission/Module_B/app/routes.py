from app import app
from flask import request, jsonify, render_template, redirect, flash, url_for
from app.log_form import LoginForm
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host = "localhost",
        user = "stayease", # often 'root'
        password = "stayease",
        database = "stayease" # The database you created for Module B
    )

@app.route('/', methods=['GET'])
def root():
    return jsonify({"message": "Welcome to test APIs"})

@app.route('/login', methods=['GET', 'POST'])
def login():
    # ==========================================
    # PATH 1: The API Requirement (For Machines)
    # ==========================================
    # If a tool like Postman or frontend JavaScript sends raw JSON data:
    if request.is_json:
        data = request.get_json()
        # Later: check your DB using data['user'] and data['password']
        return jsonify({
            "message": "Login successful",
            "session_token": "dummy_jwt_token_for_now"
        }), 200

    # ==========================================
    # PATH 2: The Web UI Requirement (For Humans)
    # ==========================================
    # If a human is using the browser, we use the WTForm
    form = LoginForm()
    
    # Did the human click "Submit" on the HTML form?
    if form.validate_on_submit():
        # The flash message shows a temporary alert on the screen
        flash('Login requested for user {}'.format(
            form.username.data))
            
        # Later: Check DB, generate token, and save it in a browser cookie/session here
            
        # Redirect the human to their portfolio so they see a web page, not raw JSON!
        return redirect(url_for('portfolio'))

    # If it's just a standard GET request, show the blank HTML form
    return render_template('login.html', title = 'Login', form = form)

@app.route('/isAuth', methods=['GET'])
def isAuth():
    return jsonify({
        "message": "User is authenticated", 
        "username": "test_student", 
        "role": "Regular User", 
        "expiry": "2026-03-15"
    })

@app.route('/portfolio', methods = ['GEt'])
def portfolio():
    user = {'username': 'User_name'}
    return render_template('pf.html', title = 'Portfolio', user = user)