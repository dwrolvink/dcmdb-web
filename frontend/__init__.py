# -- Import global modules
from flask import Flask, g

# -- Define globals
title = 'Flask Base Project'

# When running `flask run`, create_app() is a special function name that 
# will be looked for. If it exists, it will be automatically executed 
# after running this file.
# This is part of the Application Factory design pattern in Flask.

def create_app():

	# -- Initialize app
	app = Flask(__name__, instance_relative_config=True)

	# instance_relative_config=True tells the app that configuration
	# files are relative to the instance folder. The instance folder is 
	# located outside the flask package and can hold local data that 
	# shouldn’t be committed to version control, such as configuration 
	# secrets and the database file.

	# -- Load proper config
	if app.config["ENV"] == "production":
		app.config.from_object("config_local.ProductionConfig")
	else:
		app.config.from_object("config_local.DevelopmentConfig")
		print(' * Using development config')

	# -- Register blueprints
	#
	# In Flask, a blueprint is a logical structure that represents a 
	# subset of the application. 
	#
	# A blueprint can include elements such as routes, view functions, 
	# forms, templates and static files. If you write your blueprint in 
	# a separate Python package, then you have a component that 
	# encapsulates the elements related to specific feature of the 
	# application.
	#
	# Register main, this is the blueprint that handles the homepage
	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	# -- Return app to Flask to start serving files
	return app

