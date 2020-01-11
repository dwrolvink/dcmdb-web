# Run app in production mode. See run.py for production mode.
#
# Requirements:
# - uwsgi, uwsgi-plugin-python
#
# Call this script with `python serve.py`.
#
# If you're using pipenv, be sure to cd into the project folder 
# beforehand, (this file is located in the project folder),
# then call this script with `pipenv run python serve.py`

import os
import subprocess

# Change dir so that the current working directory is the project folder
# If you're using pipenv, be sure to cd into the project folder 
# beforehand. Otherwise pipenv will try to create a new venv.
script_root = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_root)

# Set the name of the app that we want to start 
os.environ['FLASK_APP'] = "frontend"

# flask run
subprocess.run(
				["uwsgi", "-s", "/tmp/flask-base-project.sock",
				"--manage-script-name", "--mount", "/=wsgi:app",
				"--http-socket", ":5000", "--plugin", "python"
				])

