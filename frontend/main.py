""" App blueprint module for handling basic pages.

Serves the following routes:
index -- the homepage
"""
import sys
sys.path.append("../flask-example-app")
from flask import Blueprint, render_template, g, current_app
from backend.app import App as Backend
from . import title
import datetime

# Initialize backend
backend = Backend()

# Initialize Blueprint
main = Blueprint('main', __name__)

# -- Routes
#
# @main.route('/') will bind the render_homepage function to any requests
# to the sites root (e.g. http://localhost/).
#
@main.route('/')
def render_homepage():
    # Set the global title variable
    g.title = current_app.config['WEBSITE_NAME'] + ' - Homepage'

    # Get date as a string
    dt = datetime.datetime.now()
    g.date = dt.strftime('%m/%d/%Y')

    # Get the template /templates/index.html and return it.
    # Note that index.html requires base.html, so index.html will be
    # inserted into base.html, and base.html will then be returned. 
    # (See the first line of index.html)
    return render_template('index.html') 

@main.route('/login', methods=['GET', 'POST'])
def render_login_page():
    # Set the global title variable
    g.title = current_app.config['WEBSITE_NAME'] + ' - Login'

    # Init form
    from .forms import LoginForm
    form = LoginForm()

    if form.validate_on_submit():
        g.title = form.username.data

    return render_template('login.html', form=form)

@main.route('/api/v1/object/<object>/<obj_id>')
def render_object_api_v1(object, obj_id):
    # Set the global title variable
    #g.title = current_app.config['WEBSITE_NAME'] + ' - Homepage'

    obj = backend.get_object_by_id(obj_id)
    g.obj = obj

    return render_template('api_v1_object_details.html') 