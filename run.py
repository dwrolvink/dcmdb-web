# Run our app in development mode. See serve.py for production mode.

# Call this script with `python run.py`.
#
# If you're using pipenv, be sure to cd into the project folder 
# beforehand, (this file is located in the project folder),
# then call this script with `pipenv run python run.py`

import os
import subprocess

# Change dir so that the current working directory is the project folder
# If you're using pipenv, be sure to cd into the project folder 
# beforehand. Otherwise pipenv will try to create a new venv.
script_root = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_root)

# Set the name of the app that we want to start 
os.environ['FLASK_APP'] = "frontend"

# By default, ENV is set to production which disables DEBUG mode and 
# avoids displaying the interactive debugger to the world, 
# meaning if you just ran your application without explicitly setting 
# FLASK_ENV, it would run in production mode.
# Setting FLASK_ENV=development enables the debugger, which should never, 
# ever be done in production!
os.environ['FLASK_ENV'] = "development"
os.environ['FLASK_RUN_HOST'] = "0.0.0.0"

# flask run
subprocess.run(["flask", "run"])