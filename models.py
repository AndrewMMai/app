#importing the necessary modules
import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import TimedSerializer as Serializer
from flask import current_app
from datetime import datetime
import hashlib
from flask import request

#database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Defining the permissions that a user/admin will have
class Permission:
    WRITE = 4
    MODERATE = 8
    ADMIN = 16

#-----------------------------CLASS User--------------------------------------
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    username=db.Column(db.String(64))
    email=db.Column(db.String(128), index=True)
    yearOfStudy= db.Column(db.String(11), index=True)
    regNumber = db.Column(db.String(64), index=True)
    phoneNumber = db.Column(db.Integer, unique=True, index=True)
    password=db.Column(db.String(128), index=True)
    #Password hashing in the User Model
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    avatar_hash = db.Column(db.String(32))
    role = db.Column(db.String(20), default = "User")
    secQuestion = db.Column(db.Text)
    secAnswer = db.Column(db.Text)
    commodity = db.relationship('Commodity', backref='author', lazy='dynamic')
    goodsAdded = db.relationship('goodsCart', backref='purchaser', lazy='dynamic')
    goodsPurchased = db.relationship('goodsPurchased', backref='purchaserer', lazy='dynamic')
    pendingIssues = db.relationship('Pending', backref='issues', lazy='dynamic')
    idss = db.relationship('Dashboard', backref='iss', lazy='dynamic')
    idss2 = db.relationship('goodsPending', backref='iss2', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.username
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self, password):
            self.password_hash = generate_password_hash(password)
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


#-----------Gravatar URL generation------------------------------------------
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()
    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or self.gravatar_hash()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)
#-----------------------------------------------------------------------------------------
    
#--evaluating whether a user has a given permission(copied to __init__.py)---------------------
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)
    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def gravatar(self, size=100, default='identicon', rating='g'):
        url = 'https://secure.gravatar.com/avatar'
        hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)
#------------------------------------------------------------------------
#---------------Commodity Model---------------------------------------------
class Commodity(db.Model):
    __tablename__ = 'commodity'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    type = db.Column(db.String(64))
    manDate = db.Column(db.String(64))
    expDate = db.Column(db.String(64))
    quantity = db.Column(db.Integer)
    oldPrice = db.Column(db.Integer)
    discPrice = db.Column(db.Integer)
    percDiscount = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    inStock = db.Column(db.String(5), default = "Yes")
    author1 = db.Column(db.Text, db.ForeignKey('users.name'))
    addDesc = db.Column(db.Text, nullable = True)
#----------------------------------------------------------------------------

#-----------------goodsCart Model------------------------------------------
class goodsCart(db.Model):
    __tablename__ = 'goodsCart'
    id = db.Column(db.Integer, primary_key=True, unique = True)
    name = db.Column(db.Text)
    type = db.Column(db.String(64))
    manDate = db.Column(db.String(64))
    expDate = db.Column(db.String(64))
    reqQuantity = db.Column(db.Integer)
    price = db.Column(db.Integer)
    percDiscount = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    added = db.Column(db.Boolean, default=True)
    buyer = db.Column(db.Integer, db.ForeignKey('users.name'))
    seller = db.Column(db.Text)
#-----------------------------------------------------------------------------
#-------------goodsPurchased Model--------------------------------------------
class goodsPurchased(db.Model):
    __tablename__ = 'goodsPurchased'
    id = db.Column(db.Integer, primary_key=True, unique = True)
    name = db.Column(db.Text)
    type = db.Column(db.String(64))
    manDate = db.Column(db.String(64))
    expDate = db.Column(db.String(64))
    reqQuantity = db.Column(db.Integer)
    price = db.Column(db.Integer)
    percDiscount = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    bought = db.Column(db.Boolean, default=True)
    claimed = db.Column(db.Boolean, default=False)
    buyer = db.Column(db.Integer, db.ForeignKey('users.name'))
    seller = db.Column(db.Text)
#-----------------------------------------------------------------------------
#-------------Pending Model---------------------------------------------------
class Pending(db.Model):
    __tablename__='pending'
    id = db.Column(db.Integer, primary_key=True, unique = True)
    name = db.Column(db.Text)
    username = db.Column(db.Text)
    issue = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
#----------------------------------------------------------------------------
#-----------Class for uploading pictures-------------------------------------
class Img(db.Model):
    __tablename__='images'
    id=db.Column(db.Integer, primary_key=True, index=True)
    img = db.Column(db.Text, nullable=True)
    mimetype = db.Column(db.Text, nullable = False)
    timestamp = db.Column(db.DateTime, default = datetime.utcnow)
    commsID = db.Column(db.Integer)
    commID = db.Column(db.Integer, db.ForeignKey('goodspending.id'))
    #data=db.Column(db.LargeBinary)
#----------------------------------------------------------------------------
#----------Class for dashboard messages--------------------------------------
class Dashboard(db.Model):
    __tablename__='dashboard'
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(50))
    sender = db.Column(db.String(50), default="Admin")
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    message = db.Column(db.Text)
    use_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
#----------------------------------------------------------------------------
#---------------CommodityPending Model---------------------------------------------
class goodsPending(db.Model):
    __tablename__ = 'goodspending'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    type = db.Column(db.String(64))
    manDate = db.Column(db.String(64))
    expDate = db.Column(db.String(64))
    quantity = db.Column(db.Integer)
    oldPrice = db.Column(db.Integer)
    discPrice = db.Column(db.Integer)
    percDiscount = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    inStock = db.Column(db.String(5), default = "Yes")
    author2 = db.Column(db.Integer, db.ForeignKey('users.name'))
    addDesc = db.Column(db.Text, nullable = True)
    ids = db.relationship('Img', backref='isess', lazy='dynamic')
#----------------------------------------------------------------------------