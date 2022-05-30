from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo

class NameForm(FlaskForm):
    name=StringField('What is your name?',validators=[DataRequired()])
    submit=SubmitField('Submit')

#----------Form for sending message to user-------------------------
class SendMessageForm(FlaskForm):
    message = TextAreaField('Type your message here*', validators=[DataRequired()])
    submit = SubmitField('Send Message')
#----------------------------------------------------------------------