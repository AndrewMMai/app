from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, ValidationError
from wtforms import IntegerField, BooleanField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from app.models import User

#-----------------Commodity form---------------------------------------------
class CommodityForm(FlaskForm):
    name = StringField('Commodity Name*', validators=[Length(0, 64), DataRequired()])
    type = SelectField("Type of Commodity*", choices=[
        ('Electronics',"Electronics"), ('Cutlery',"Cutlery"), ('Stationery',"Stationery"), 
        ('Foodstuffs',"Foodstuffs")], validators=[DataRequired()])
    manDate = StringField('Date of manufacture* (could be the year or date in preferred format)', validators=[Length(0,16)])
    expDate = StringField('Date of expiry (could be None for Electronics, Cutlery and Stationery)*', validators=[Length(0,16), DataRequired()])
    quantity = IntegerField('Quantity on sale', validators=[DataRequired()])
    oldPrice = IntegerField('Old Price per unit in Kenyan Shillings*', validators=[DataRequired()])
    discPrice = IntegerField('Discounted Price per unit in Kenyan Shillings*', validators=[DataRequired()])
    addDesc = TextAreaField('Add any additional descriptions here: ')
    submit = SubmitField('Submit')
#-----------------------------------------------------------------------------
#---------------Shopping cart quantity form-----------------------------------
class QuantityForm(FlaskForm):
    goodQuantity = IntegerField('How many would you like to buy?*',validators=[DataRequired()])
    submit = SubmitField('Confirm')
#-----------------------------------------------------------------------------
#----------Form for granting admin priveledges--------------------------------
class PendingForm(FlaskForm):
    issue = SelectField('Which issue would you like to be addressed? *', choices =
        [('Grant admin priveledges',"Grant admin priveledges"),
         ('Relinquish admin priveledges', "Relinquish admin priveledges")], validators=[DataRequired()])
    submit = SubmitField('Confirm')
#------------------------------------------------------------------------------
#-------Search Form------------------------------------------------------------
class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#----------Form for granting admin priveledges--------------------------------
class GeneralForm(FlaskForm):
    issue = TextAreaField('Which general issue would you like to be addressed? *', validators=[DataRequired()])
    submit = SubmitField('Confirm')
#------------------------------------------------------------------------------

