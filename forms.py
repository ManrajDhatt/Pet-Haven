from wtforms import FileField, StringField, PasswordField, SubmitField, TextAreaField, FloatField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo

from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed  

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    location=StringField('Location',validators=[DataRequired()])
    date = StringField('Date', validators=[DataRequired()])
    eligibility=StringField('Eligibility',validators=[DataRequired()])
    prizes=StringField('Prizes',validators=[DataRequired()])
    fee = FloatField('Fee', validators=[DataRequired()])
    image = FileField('Event Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])  

    submit = SubmitField('Add Event')


class RegistrationEventForm(FlaskForm):
    pet_name = StringField('Pet Name', validators=[DataRequired()])
    pet_type = StringField('Pet Type', validators=[DataRequired()])
    pet_age=StringField('Pet Age',validators=[DataRequired()])
    submit = SubmitField('Register')
