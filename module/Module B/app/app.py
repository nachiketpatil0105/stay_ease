# app.py
from flask import Flask, jsonify, render_template

# Import your custom blueprints
from routes_auth import auth_bp
from routes_portfolio import portfolio_bp
from routes_admin import admin_bp

app = Flask(__name__)

# Register the routes with the main app
app.register_blueprint(auth_bp)
app.register_blueprint(portfolio_bp)
app.register_blueprint(admin_bp)

# --- Frontend & Base Routes ---
@app.route('/', methods=['GET'])
def welcome():
    return jsonify({"message": "Welcome to test APIs"}), 200

@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)