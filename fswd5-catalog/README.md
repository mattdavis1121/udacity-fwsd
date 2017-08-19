# fswd5-catalog
An application that provides a list of items within a variety of categories as
well as provide a user registration and authentication system.

## Configuration
Configuration settings can be found in config.py. The secret key should be
replaced with a secure secret key, which can be randomly generated.

The app is currently configured to use SQLite on the back-end, but this can be
changed by editing the SQLALCHEMY_DATABASE_URI in config.py.


## Setup
    >> mkvirtualenv catalog
    >> pip install -r requirements.txt
    >> python make_db.py

## Running the app
The app currently runs on Flask's built-in development server. Per the Flask
documentation, it's best not to use this in a production environment. To run
the app on the dev server:
    >> cd [project root directory]
    >> python run.py
