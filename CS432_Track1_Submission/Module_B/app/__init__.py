from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'stayease_project'

from app import routes