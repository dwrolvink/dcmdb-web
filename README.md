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

