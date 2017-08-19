# Place all Flask configs here

import os
basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'This is my random string'

# Define database configs
SQLALCHEMY_DATABASE_URI = 'postgresql://catalog:udacity@localhost:5432/catalog'
SQLALCHEMY_TRACK_MODIFICATIONS = False
FLASK_DEBUG=1
