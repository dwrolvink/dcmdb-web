# DCMDB-Frontend


# Running this project
## Test/Debug mode
### On a Linux machine:
```bash
# Install prerequisites
# - install python and pip through your package manager of choice
pip install pipenv

# Get the code
cd <myProjectsFolder>
git clone git@gitlab.com:dwrolvink1/flask-base-project.git

# Initiate virtual environment and download pip modules in the process
cd flask-base-project
pipenv install

# Enter the virtual environment, and start the app
pipenv shell
export FLASK_APP='application'
export FLASK_ENV='development' # default is production
flask run

# Exit app and exit virtual env
# -  Ctrl+C
exit
```

After having ran this app once, you can start it up more quickly by 
doing:
```bash
cd <myProjectsFolder>/flask-base-project
pipenv run python run.py   # development
pipenv run python serve.py # production
```

### On a windows machine:
```powershell
# Install prerequisites
# - Install python 3.8 64 bit, choose add to path and your install 
#   location (install for all users is recommended)
# - pip is installed with python

# I'm skipping pipenv because of bugginess at the time of writing
# Install requirements globally by hand:
pip install flask

# Get the code
cd <myProjectsFolder>
git clone git@gitlab.com:dwrolvink1/flask-base-project.git

# Start the app
cd flask-base-project
$env:flask_app = 'application'
$env:flask_env = 'development' # default is production
flask run
```
After having ran this app once, you can start it up more quickly by 
doing:
```powershell
cd <myProjectsFolder>/flask-base-project
python run.py   # development
python serve.py # production
```

## Production setup
First, install uwsgi and  uwsgi-plugin-python.

```bash
# install 
cd <myProject>
python serve.py
```
See serve.py for more information about the production setup
