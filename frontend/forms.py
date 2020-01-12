from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, HiddenField
from wtforms.validators import InputRequired, Length, Optional

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
                            'Handle', 
                            validators=[
                                InputRequired(), 
                                Length(min=5, max=200)
                                ]
                            )
    object_value = StringField(
                            'Name (Leave empty if same as handle)', 
                            validators=[
                                Length(min=0, max=200)
                                ]
                            )
    submit = SubmitField('Submit')

class CreateObjectTypeForm(FlaskForm):
    object_type_handle = StringField(
                            'Handle', 
                            validators=[
                                InputRequired(), 
                                Length(min=5, max=200)
                                ]
                            )
    object_type_name = StringField(
                            'Name (Leave empty if same as handle)', 
                            validators=[
                                Length(min=0, max=200)
                                ]
                            )
    object_type_description = StringField(
                            'Description'
                            )                            
    submit = SubmitField('Submit')

class AddPropertyForm1(FlaskForm):
    object_type_handle= SelectField(
                            'Object', validators=[Optional()]
                            )                                         
    submit1 = SubmitField('Submit')    

class AddPropertyForm2(FlaskForm):
    object_type_handle = StringField(
                            'Object type',
                            validators=[
                                InputRequired()
                                ]
                            )
    object_instance_handle= SelectField(
                            'Object',
                            validators=[
                                InputRequired()
                                ]                            
                            )
    submit2 = SubmitField('Submit')      