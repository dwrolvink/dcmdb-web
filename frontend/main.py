""" App blueprint module for handling basic pages.

Serves the following routes:
index -- the homepage
"""
from .integrator import Integrator
index = Integrator() 

# Initialize Blueprint
main = index.Blueprint('main', __name__)

# -- Routes
#
# @main.route('/') will bind the render_homepage function to any requests
# to the sites root (e.g. http://localhost/).
#
@main.route('/')
def render_homepage():
    # Set the global title variable
    index.g.title = index.current_app.config['WEBSITE_NAME'] + ' - Homepage'

    # Get date as a string
    dt = index.datetime.datetime.now()
    index.g.date = dt.strftime('%m/%d/%Y')

    # Get the template /templates/index.html and return it.
    # Note that index.html requires base.html, so index.html will be
    # inserted into base.html, and base.html will then be returned. 
    # (See the first line of index.html)
    return index.render_template('index.html') 

@main.route('/login', methods=['GET', 'POST'])
def render_login_page():
    # Set the global title variable
    index.g.title = index.current_app.config['WEBSITE_NAME'] + ' - Login'

    # Init form
    from .forms import LoginForm
    form = LoginForm()

    if form.validate_on_submit():
        index.g.title = form.username.data

    return index.render_template('login.html', form=form)
