from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, current_user
from . import auth
from ..models import Pending, User, Dashboard #check and confirm db
from .forms import LoginForm, RegistrationForm, Email, AccountRecovery#check and confirm registration form
from app.email import send_email
from ..__init__ import db
from ..email import send_email


@auth.route('/index/')
def index2():
    messages = Dashboard.query.filter_by(name = current_user.name).order_by(Dashboard.timestamp.desc()).first()
    return render_template('index.html', messages = messages)
#--------------------------------------------------------------------------
#-------------Welcoming message--------------------------------------------
@auth.route('/')
def index():
    return render_template('index.html')
#--------------------------------------------------------------------------
@auth.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Invalid email!')
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('auth.index2')
            flash('Login successful.')
            if current_user.confirmed == False:
                flash('Your account will be confirmed shortly!')
            return redirect(next)
        else:
            flash('Incorrect password!')
    return render_template('auth/login.html', form=form)
#--------------------------------------------------------------------------

#------------------------Log out route-------------------------------------
from flask_login import logout_user, login_required
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.index'))
#--------------------------------------------------------------------------

#---------------------------user registration route------------------------
@auth.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data,
            email=form.email.data,
            username=form.username.data,
            password=form.password.data,
            yearOfStudy=form.yearOfStudy.data,
            regNumber=form.regNumber.data,
            phoneNumber=form.phoneNumber.data,
            secQuestion=form.secQuestion.data,
            secAnswer=form.secAnswer.data)
        op1 = User.query.filter_by(username=form.username.data).first()
        op2 = User.query.filter_by(regNumber=form.regNumber.data).first()
        op3 = User.query.filter_by(phoneNumber=form.phoneNumber.data).first()
        op4 = User.query.filter_by(email=form.email.data).first()
        if op1:
            flash('Username already taken!')
            return render_template('auth/register.html', form=form)
        elif op2:
            flash('Registration number already taken!')
            return render_template('auth/register.html', form=form)
        elif op3:
            flash('Phone number already taken!')
            return render_template('auth/register.html', form=form)
        elif op4:
            flash('Email already taken!')
            return render_template('auth/register.html', form=form)
        else:
            issues = Pending(name = form.name.data,
                username = form.username.data,
                issue = "Confirm user registration." )
            db.session.add(user)
            db.session.add(issues)
            db.session.commit()
            flash('You have been registered. Please log in and await confirmation.')
            return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)
#------------------------------------------------------------------------
#------Route for recovering account----------------------------------------
@auth.route('/forgot', methods=['GET', 'POST'])
def forgot():
    form = Email()
    if form.validate_on_submit():
        userf = User.query.filter_by(email=form.userEmail.data).first()
        if userf:
            email = userf.email
            return redirect(url_for('auth.question', email = email))
        else:
            flash('No such email exists!')
    return render_template('email.html', form = form)
#--------------------------------------------------------------------------
#---------Route for asking security question-------------------------------
@auth.route('/question/<email>', methods=['GET', 'POST'])
def question(email):
    userf = User.query.filter_by(email=email).first()
    question = userf.secQuestion
    form = AccountRecovery()
    if form.validate_on_submit():
        if form.secAnswer.data == userf.secAnswer:
            flash('Correct! Please change your account details accordingly.')
            return redirect(url_for('main.edit_profile2', id = userf.user_id))
        else:
            flash('Wrong answer. Try again')
    return render_template('recovery.html', form = form, question = question)
#-----------------------------------------------------------------------------
