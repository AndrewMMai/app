#Application package constructor--------------------------------
from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from app.config import config
from app.forms import NameForm
#--------------login route imports-----------------------------------------------
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, current_user, AnonymousUserMixin
from . import auth
from .models import User
from app.auth.forms import LoginForm, RegistrationForm #check and confirm registration form
from app.email import send_email
#---------------------------------------------------------------------------------
app = Flask(__name__)

#Flask-Login Initialization-------------------------------------------
from flask_login import LoginManager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


bootstrap = Bootstrap()
mail = Mail()
db = SQLAlchemy()
def create_app(config_name):
    #app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    # attach routes and custom error pages here
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is not None and user.verify_password(form.password.data):
                login_user(user, form.remember_me.data)
                next = request.args.get('next')
                if next is None or not next.startswith('/'):
                    next = url_for('main.index')
                return redirect(next)
            flash('Invalid email or password.')
        return render_template('auth/login.html', form=form)
#--------------------------------------------------------------------------
    from flask import Flask, render_template, session, redirect, url_for, flash
    #@app.route('/', methods=['GET', 'POST'])
    #def index():
        #form = NameForm()
        #if form.validate_on_submit():
            #old_name = session.get('name')
            #if old_name is not None and old_name != form.name.data:
                #flash('Looks like you have changed your name!')
            #session['name'] = form.name.data
            #return redirect(url_for('index'))
        #return render_template('index.html',
            #form = form, name = session.get('name'))
    
    #@app.route('/login', methods=['GET', 'POST'])#might need to change app to auth
    #def login():
        #form = LoginForm()
        #if form.validate_on_submit():
            #user = User.query.filter_by(email=form.email.data).first()
            #if user is not None and user.verify_password(form.password.data):
                #login_user(user, form.remember_me.data)
                #next = request.args.get('next')
                #if next is None or not next.startswith('/'):
                    #next = url_for('main.index')
                #return redirect(next)
            #flash('Invalid username or password.')
        #return render_template('auth/login.html', form=form)

    @app.route('/about/')
    def about():
        return render_template('about.html')

    @app.route('/contacts/')
    def contacts():
        return render_template('contacts.html')

    @app.route('/catalog/')
    def catalog():
        return render_template('catalog.html')

    @app.route('/catalog/electronics')
    def commoditypg1():
        return render_template('electronics.html')

    @app.route('/catalog/cutlery')
    def commoditypg2():
        return render_template('cutlery.html')

    @app.route('/catalog/foodstuffs')
    def commoditypg3():
        return render_template('foodstuffs.html')

    @app.route('/catalog/stationery')
    def commoditypg4():
        return render_template('foodstuffs.html')

    #main blueprint registration
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    #authentication blueprint registration
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
#-----------------------------------------------------------------

#-------------User loader function--------(copied from models.py)-----------------
#from app.__init__ import login_manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.user_id==user_id).first()
#--------------------------------------------------------------------------------

#--------evaluating whether a user has a given permission----------------------
    #def can(self, perm):
        #return self.role is not None and self.role.has_permission(perm)
    #def is_administrator(self):
        #return self.can(Permission.ADMIN)
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    def is_administrator(self):
        return False
login_manager.anonymous_user = AnonymousUser
#-----------------------------------------------------------------------------