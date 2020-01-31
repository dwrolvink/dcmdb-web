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

class CreateRecordForm(FlaskForm):
    record_handle = StringField('Handle', validators=[InputRequired(), Length(min=1, max=200)])
    record_value = StringField( 'Name/Value (Leave empty if same as handle)', 
                                validators=[Length(min=0, max=200)])
    submit = SubmitField('Submit')

class CreateRecordClassForm(FlaskForm):
    class_handle      = StringField('Handle', 
                        validators=[InputRequired(), Length(min=1, max=200)])
    class_name        = StringField('Name (Leave empty if same as handle)', 
                         validators=[Length(min=0, max=200)])                      
    class_description = StringField('Description')                  
    submit = SubmitField('Submit')

class CreateValueTypeForm(FlaskForm):
    class_handle      = StringField('Handle', 
                        validators=[InputRequired(), Length(min=1, max=200)])
    class_name        = StringField('Name (Leave empty if same as handle)', 
                         validators=[Length(min=0, max=200)])                      
    class_description = StringField('Description')
    class_unit        = StringField('Unit (will be displayed as suffix)')                  
    submit = SubmitField('Submit')


class AddPropertyForm_choose_class(FlaskForm):
    class_handle   = SelectField('Object', validators=[Optional()])                                         
    submit1        = SubmitField('Submit')    

class AddPropertyForm_choose_record(FlaskForm):
    class_handle   = StringField('Class',validators=[InputRequired()])                      
    record_handle  = SelectField('Record', validators=[InputRequired()])
    submit2        = SubmitField('Submit')      

class AddPropertyForm_choose_value(FlaskForm):
    class_handle  = StringField('Class', validators=[InputRequired()])
    value         = StringField('Value', validators=[InputRequired()])
    submit3       = SubmitField('Submit') 

class TestForm(FlaskForm):
    sel_class_handle  = SelectField('Class', validators=[Optional()]) 
    sel_record_handle = SelectField('Record', validators=[Optional()]) 
    value         = StringField('Value', validators=[Optional()])
    label         = StringField('Label', validators=[Optional()])