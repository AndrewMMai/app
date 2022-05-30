#main script
import os
from app import create_app, db
from app.models import User#, Role
from flask_migrate import Migrate
from flask import Flask
from app.main.forms import SearchForm

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User)#, Role=Role)

#------Route for passing stuff into the HTML file containing search form-----
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)
#----------------------------------------------------------------------------

#------------Database configuration-------------------------------
#import os
#from flask_sqlalchemy import SQLAlchemy
#basedir = os.path.abspath(os.path.dirname(__file__))    
#app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] =\
    #'sqlite:///' + os.path.join(basedir, 'data.sqlite')
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#db = SQLAlchemy(app)
#-----------------------------------------------------------------


