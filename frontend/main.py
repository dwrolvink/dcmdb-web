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

@main.route('/reset_database')
def reset_database():
    index.scripts["reset_database"].run(index.backend)
    index.backend.process_input("backend/data/input.stid")
    return render_homepage()


@main.route('/show_input')
@main.route('/show_input/<file_name>')
def show_input(file_name=""):
    if file_name == "":
        file_name = "input"

    input_file = "backend/data/{}.stid".format(file_name)

    output = "<pre>"
    
    with open(input_file) as f:
        for line in f:
            line = line.replace("\t","  ")

            if len(line) == 0:
                output += line
            elif line[0] == "#":
                output += '<span style="color:green">'+line+"</span>"
            elif line[0] == ">":
                url = line.replace("> ", "").replace(".stid", "").strip()
                output += '<a href="show_input/{}">'.format(url)
                output += '<span style="color:red">'+line+"</span></a>"                    
            elif line[0] == "+":
                output += '<span style="font-weight:bold">'+line+"</span>"   
            elif ":" in line:
                parts = line.split(":")
                output += parts[0]
                output += ':<span style="color:red">'+parts[1]+"</span>"                                          
            else:
                output += line 
    output += "</pre>"
    return output
