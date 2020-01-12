from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length

class LoginForm(FlaskForm):
	username = StringField(
							'username', 
							validators=[
								InputRequired(), 
								Length(min=3, max=20)
								]
							)
	password = PasswordField(
							'password', 
							validators=[
								InputRequired(), 
								Length(min=8, max=20)
								]
							)
	submit = SubmitField('Submit')

class CreateObjectForm(FlaskForm):
	object_handle = StringField(
							'object_handle', 
							validators=[
								InputRequired(), 
								Length(min=1, max=200)
								]
							)
	object_value = StringField(
							'object_value', 
							validators=[
								Length(min=0, max=200)
								]
							)
	submit = SubmitField('Submit')