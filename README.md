# DCMDB-Web
- [Frontend](docs/frontend.md)
- [Backend](docs/backend.md)

# Introduction
DCMDB is a simple tool to create objects and the relationships between them.
The main sellingpoint of dcmdb is that you can create any kind of object
and object-object relationship straight from the application.

Juggling dynamic relationships with performance is really hard (for me at least),
so don't expect good performance from this system when you have a massive amount
of objects.

# Architecture
The frontend is a Flask application that serves the website to interact with
the backend, which is a plain Python application.

The backend requires sqlite3 to be installed. The frontend has more complex
requirements which can be installed using pipenv (among others). See the frontend 
readme for more information.

# Installation
```bash
# first install python3, pip
# then:
pip install pipenv

# Get code
git clone https://github.com/dwrolvink/dcmdb-web.git

# Install frontend requirements
cd dcmdb-web
pipenv install

# Reset the database (optional, when running the first time)
python reset_database.py

# Copy config.py to config_local.py and edit the values
cp config.py config_local.py

# Start the application (development mode)
pipenv run python run.py
```

# Resetting the database
When you are playing around with this system, it's nice to roll back now and then.
In dcmdb-web/backend/data, you'll find an input file. If you edit this file to add types/objects, those will be created in a fresh database when you call reset_database.py

# About the frontend
For more in-depth information, see [Frontend](docs/frontend.md).
