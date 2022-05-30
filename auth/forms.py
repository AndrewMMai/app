#------------------------Login form--------------------------------------------
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms import SelectField
from wtforms.validators import DataRequired, Length, Email

class LoginForm(FlaskForm):
    email = StringField('Email*', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password*', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')
#--------------------------------------------------------------------------------

#----------------------------user registration form------------------------------
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError, IntegerField
from ..models import User

class RegistrationForm(FlaskForm):
    name = StringField('Full Name*', validators=[DataRequired()])
    username = StringField('Username*', validators=[
        Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
        'Usernames must have only letters, numbers, dots or '
        'underscores'), DataRequired()])
    email = StringField('Email*', validators=[DataRequired(), Length(1, 64), Email()])
    yearOfStudy = SelectField('Year of Study*', choices=[
        ('First Year',"First Year"), ('Second Year',"Second Year"), ('Third Year',"Third Year"), 
        ('Fourth Year',"Fourth Year"), ('Fifth Year',"Fifth Year")], validators=[DataRequired()])
    regNumber=StringField('Registration Number*(Type "TRADER" if not university student)', validators=[DataRequired(),
        Length(1, 15), Regexp('^[A-Za-z][A-Za-z0-9/]*$')])
    phoneNumber = StringField('Phone Number*', validators=[DataRequired(), 
        Length(1, 10) ])
    secQuestion = TextAreaField('Your security question*(In case of forgotten password)',
        validators=[DataRequired(), Length(1, 100)])
    secAnswer = TextAreaField('Your security answer*(In case of forgotten password)',
        validators=[DataRequired(), Length(1, 100)])
    password = PasswordField('Password*', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password*', validators=[DataRequired()])
    submit = SubmitField('Register')

class EditProfileForm(FlaskForm):
    name = StringField('Full Name*', validators=[DataRequired()])
    username = StringField('Username*', validators=[
        Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
        'Usernames must have only letters, numbers, dots or '
        'underscores'), DataRequired()])
    email = StringField('Email*', validators=[DataRequired(), Length(1, 64), Email()])
    yearOfStudy = SelectField('Year of Study*', choices=[ 
        ('First Year',"First Year"), ('Second Year',"Second Year"), ('Third Year',"Third Year"), 
        ('Fourth Year',"Fourth Year"), ('Fifth Year',"Fifth Year")], validators=[DataRequired()])
    regNumber=StringField('Registration Number*', validators=[DataRequired(),
        Length(1, 15), Regexp('^[A-Za-z][A-Za-z0-9/]*$')])
    phoneNumber = StringField('Phone Number*', validators=[DataRequired(), 
        Length(1, 10) ])
    secQuestion = TextAreaField('Your security question*(In case of forgotten password)',
        validators=[DataRequired(), Length(1, 100)])
    secAnswer = TextAreaField('Your security answer*(In case of forgotten password)',
        validators=[DataRequired(), Length(1, 100)])
    password = PasswordField('Password*', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password*', validators=[DataRequired()])
    submit = SubmitField('Make changes')
#--------------------------------------------------------------------------------
#-------------Profile editing form for Administrators------------------------
class EditProfileAdminForm(FlaskForm):
    #name = StringField('Real name*', validators=[Length(0, 64)])
    email = StringField('Email*', validators=[DataRequired(), Length(1, 64),
        Email()])
    username = StringField('Username*', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
        'Usernames must have only letters, numbers, dots or '
            'underscores')])
    yearOfStudy = SelectField('Year of Study*', choices=[
        ('First Year',"First Year"), ('Second Year',"Second Year"), ('Third Year',"Third Year"), 
        ('Fourth Year',"Fourth Year"), ('Fifth Year',"Fifth Year")], validators=[DataRequired()])
    regNumber=StringField('Registration Number', validators=[DataRequired(),
        Length(1, 15), Regexp('^[A-Za-z][A-Za-z0-9/]*$')])
    phoneNumber = StringField('Phone Number', validators=[DataRequired(), 
        Length(1, 10) ])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role*', choices=[('User',"User"),('Administrator',"Administrator")], validators=[DataRequired()])
    submit = SubmitField('Submit')
#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
class Email(FlaskForm):
    userEmail = StringField('Input your email*', validators = [DataRequired(),
        Length(1, 50)])
    submit = SubmitField('Submit')
#------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
class AccountRecovery(FlaskForm):
    secAnswer = StringField('Answer*', validators = [DataRequired(),
        Length(1, 100)])
    submit = SubmitField('Submit')
#------------------------------------------------------------------------------------

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
    def validate_regnumber(self, field):
        if User.query.filter_by(regNumber=field.data).first():
            raise ValidationError('Registration number already in use.')
    def validate_password(self, field):
        if User.query.filter_by(password=field.data).first():
            raise ValidationError('Password already in use.')
#-------------------------------------------------------------------------------