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