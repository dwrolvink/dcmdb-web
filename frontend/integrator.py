# Backend integration
import sys
sys.path.append("../flask-example-app")
from backend.app import App as Backend
import backend.scripts.reset_database 

# Flask general
from flask import Blueprint, render_template, g, current_app

# Frontend __init__ integration
from . import title

# General
import datetime

class Integrator():
    def __init__(self):
        self.backend = Backend()
        self.Blueprint = Blueprint
        self.render_template = render_template
        self.g = g
        self.current_app = current_app
        self.title = title
        self.datetime = datetime

        self.scripts = {}
        self.scripts["reset_database"] = backend.scripts.reset_database


