from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Define the WSGI application object
app = Flask(__name__)

# Import configurations from external file (config.py)
app.config.from_object('config')

# Create database
db = SQLAlchemy(app)

# Enable Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "index"

# Place views import at bottom of file to avoid circular imports
from app import views, models

@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, models=models)
