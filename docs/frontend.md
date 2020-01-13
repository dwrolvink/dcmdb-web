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
git clone git@github.com:dwrolvink/dcmdb-web.git

# Initiate virtual environment and download pip modules in the process
cd dcmdb-web
pipenv install

# Start the app
pipenv run python run.py

# Exit app
# -  Ctrl+C
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
git clone git@github.com:dwrolvink/dcmdb-web.git

# Start the app
cd dcmdb-web
$env:flask_app = 'application'
$env:flask_env = 'development' # default is production
flask run
```
After having ran this app once, you can start it up more quickly by 
doing:
```powershell
cd <myProjectsFolder>/dcmdb-web
python run.py   # development
python serve.py # production
```

## Production setup
First, install uwsgi and  uwsgi-plugin-python.

If you didn't do it yet in the previous steps, install pipenv:

```bash
cd <myProject>
pipenv install
```

Then, open dcmdb-web/serve.py, and change the value for venv_location.
Instructions on how to get that value can be found as comments above this
value.

```bash
cd <myProject>
pipenv run python serve.py
```

See serve.py for more information about the production setup
