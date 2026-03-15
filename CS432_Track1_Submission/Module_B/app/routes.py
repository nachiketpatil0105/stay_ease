from app import app
from flask import jsonify 

@app.route('/')
def root():
    return jsonify({"message": "Welcome to test APIs"})

@app.route('/login', methods = ['Post'])
def login():
    pass

@app.route('/isAuth', methods = ['Get'])
def isAuth():
    pass