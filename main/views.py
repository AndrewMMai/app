from flask import request
from datetime import datetime
from email.policy import default
from genericpath import exists
from sqlite3 import Timestamp
from flask import render_template, session, redirect, url_for, flash, abort, Response
from . import main
from app.forms import SendMessageForm
from app.models import db, goodsPending #-----was from ..
from app.models import Dashboard, User, Commodity, goodsCart, Pending, goodsPurchased, Img, goodsPending#, Upload, Permission, Role
from app.auth.forms import LoginForm, EditProfileAdminForm, EditProfileForm
from app.main.forms import CommodityForm, GeneralForm, QuantityForm, PendingForm, SearchForm
from flask_login import login_user, login_required, current_user
#from app.decorators import admin_required
#from app.random import searchterm
from werkzeug.utils import secure_filename

ROWS_PER_PAGE = 1

    
@main.route('/about/')
def about():
    return render_template('about.html')

#---------Landing page route------------------------------------------
@main.route('/')
def index():
    if current_user.is_anonymous:
        return render_template('index.html')
    else:
        messages = Dashboard.query.filter_by(name = current_user.name).order_by(
            Dashboard.timestamp.desc()).first()
        if messages is None:
            return render_template('index.html', messages=None)
    return render_template('index.html', messages=messages)
#---------------------------------------------------------------------

@main.route('/contacts/')
@login_required
def contacts():
    return render_template('contacts.html')

@main.route('/catalog/')
@login_required
def catalog():
    return render_template('catalog.html')

@main.route('/catalog/electronics/')
@login_required
def commoditypg1():
    commodities = Commodity.query.filter_by(type='Electronics').order_by(
        Commodity.timestamp.desc()).all()
    if commodities is None:
        return render_template('electronics.html', commodities = None)
    return render_template('electronics.html', commodities = commodities)

@main.route('/catalog/cutlery/')
@login_required
def commoditypg2():
    commodities = Commodity.query.filter_by(type='Cutlery').order_by(
        Commodity.timestamp.desc()).all()
    if commodities is None:
        return render_template('cutlery.html', commodities = None)
    return render_template('cutlery.html', commodities = commodities)

@main.route('/catalog/foodstuffs/')
@login_required
def commoditypg3():
    commodities = Commodity.query.filter_by(type='Foodstuffs').order_by(
        Commodity.timestamp.desc()).all()
    if commodities is None:
        return render_template('foodstuffs.html', commodities = None)
    return render_template('foodstuffs.html', commodities = commodities)

@main.route('/catalog/stationery/', methods=['GET','POST'])
@login_required
def commoditypg4():
    commodities = Commodity.query.filter_by(type='Stationery').order_by(
        Commodity.timestamp.desc()).all()
    if commodities is None:
        return render_template('stationery.html', commodities = None)
    return render_template('stationery.html', commodities = commodities)

#----------------edit profile route--------------------------------
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.yearOfStudy = form.yearOfStudy.data
        current_user.regNumber = form.regNumber.data
        current_user.phoneNumber = form.phoneNumber.data
        current_user.password = form.password.data
        current_user.secQuestion = form.secQuestion.data
        current_user.secAnswer = form.secAnswer.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.email.data = current_user.email
    form.username.data = current_user.username
    form.yearOfStudy.data = current_user.yearOfStudy
    form.regNumber.data = current_user.regNumber
    form.phoneNumber.data = current_user.phoneNumber
    form.secQuestion.data = current_user.secQuestion
    form.secAnswer.data = current_user.secAnswer 
    return render_template('edit_profile.html', form=form)
#--------------------------------------------------------------------------

#--------------edit profile route for administrators-----------------------
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = form.role.data
        user.regNumber = form.regNumber.data
        user.phoneNumber = form.phoneNumber.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role
    form.regNumber.data = user.regNumber
    form.phoneNumber.data = user.phoneNumber
    return render_template('edit_profile.html', form=form, user=user)
#-----------------------------------------------------------------------------

#-------Route for adding commodities------------------------------------------
@main.route('/add-commodity/', methods=['GET', 'POST'])
@login_required
def addCommodity():
    form = CommodityForm()
    if current_user.is_authenticated and form.validate_on_submit():#was --is.authenticated()
        commodity = goodsPending(name=form.name.data,
            type = form.type.data,
            manDate = form.manDate.data,
            expDate = form.expDate.data,
            quantity = form.quantity.data,
            oldPrice = form.oldPrice.data,
            discPrice = form.discPrice.data,
            percDiscount = round((((form.oldPrice.data)-(form.discPrice.data))/(form.oldPrice.data))*100),
            author2=current_user.name,
            addDesc = form.addDesc.data) #was previously current_user._get_current_object()
        issuess = Pending(name = current_user.name,
            username = current_user.username,
            issue = "Commodity uploaded for review.")
        db.session.add(issuess)
        db.session.add(commodity)
        db.session.commit()
        flash('Please also include a picture. Your post will be deleted otherwise!')
        return render_template('upload_pics.html')
    commodities = Commodity.query.order_by(Commodity.timestamp.desc()).all()
    return render_template('add_commodity.html', form=form, commodities=commodities)
#-------------------------------------------------------------------------------

#----------Profile page route with commodity posts-----------------------------
@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    commodities = user.commodity.order_by(Commodity.timestamp.desc()).all()
    user1_role = current_user.role
    bout = goodsPurchased.query.filter_by(buyer = user.name).all()
    bout1 = goodsPending.query.filter_by(author2 = user.name).all()
    return render_template('user.html', user=user, commodities=commodities,
         role = user1_role, bout = bout, bout1 = bout1)
#-------------------------------------------------------------------------------

#-----------------Shopping cart Page--------------------------------------------
@main.route('/shopping_cart/')
@login_required
def shopping():
    commodities = goodsCart.query.filter_by(added=True).all()
    return render_template('shopping_cart.html', commodities = commodities)
#-------------------------------------------------------------------------------

#------------------Payment Page-------------------------------------------------
@main.route('/payment_page/')
@login_required
def payment():
    commodities = goodsCart.query.filter_by(added=True).all()
    return render_template('payment_page.html', commodities = commodities)
#-------------------------------------------------------------------------------

#-----------------Route for deleting a commodity--------------------------------
@main.route('/delete_commodity/<id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    comm=Commodity.query.filter_by(id=id).first()
    comm10=goodsCart.query.filter_by(id=id).first()
    comm30=goodsPending.query.filter_by(id=id).first()
    if current_user.is_authenticated:
        if comm != None:
            name = comm.author1
            user = User.query.filter_by(name=name).first()
            del4 = Img.query.filter_by(id=comm.id).first()
            username = user.username
            db.session.delete(comm)
            if del4:
                db.session.delete(del4)
            db.session.commit()
            if comm10 != None:
                db.session.delete(comm10)
                db.session.commit()
            flash("The commodity has been deleted and is no longer on sale!")
            return redirect(url_for('.user', username = username))
        elif comm30 != None:
            name = comm30.author2
            user = User.query.filter_by(name=name).first()
            username = user.username
            db.session.delete(comm30)
            db.session.commit()
        flash("The commodity has been deleted!")
        return redirect(url_for('.user', username = username))
    commodities = user.commodity.order_by(Commodity.timestamp.desc()).all()
    user1_role = current_user.role
    bout = goodsPurchased.query.filter_by(buyer = current_user.name).all()
    return render_template('user.html', user=user, commodities=commodities, role = user1_role, bout = bout)
    
#--------------------------------------------------------------------------------

#--------------------Route for adding to shopping cart---------------------------
@main.route('/add-cart/<id>', methods=['GET', 'POST'])
@login_required
def add_to_cart(id):
    commodities=Commodity.query.filter_by(id=id).first()
    form = QuantityForm()
    if form.validate_on_submit():
        req = goodsCart(id = commodities.id,
            name = commodities.name,
            type = commodities.type,
            manDate = commodities.manDate,
            expDate = commodities.expDate,
            reqQuantity = form.goodQuantity.data,
            price = (form.goodQuantity.data)*commodities.discPrice,
            percDiscount = commodities.percDiscount,
            timestamp = commodities.timestamp,
            buyer = current_user.name,
            seller = commodities.author1)
        if form.goodQuantity.data <= commodities.quantity and form.goodQuantity.data>0:
            db.session.add(req)
            db.session.commit()
            commodities = goodsCart.query.filter_by(added=True).all()
            flash("The commodity has been added to the shopping cart!")
            return render_template('shopping_cart.html', commodities = commodities)
        else:
            flash("Cannot add required quantity to shopping cart! Check the quantity on sale and try again")
    return render_template('select-quantity.html', form = form)
#------------------------------------------------------------------------

#-----------Route for changing quantity req in cart----------------------
@main.route('/change-quantity/<id>', methods=['GET', 'POST'])
@login_required
def change_quantity(id):
    oldComm = goodsCart.query.filter_by(id=id).first()
    commodities=Commodity.query.filter_by(id=id).first()
    form = QuantityForm()
    if form.validate_on_submit():
        change = goodsCart(id = oldComm.id,
            name = oldComm.name,
            type = oldComm.type,
            manDate = oldComm.manDate,
            expDate = oldComm.expDate,
            reqQuantity = form.goodQuantity.data,
            price = (form.goodQuantity.data)*commodities.discPrice,
            percDiscount = oldComm.percDiscount,
            timestamp = oldComm.timestamp,
            buyer = current_user.name,
            seller = commodities.author1)
        if form.goodQuantity.data <= commodities.quantity and form.goodQuantity.data>0:
            db.session.delete(oldComm)
            db.session.add(change)
            db.session.commit()
            commodities = goodsCart.query.filter_by(added=True).all()
            flash("Quantity of goods to be bought has been changed!")
            return render_template('shopping_cart.html', commodities = commodities)
        else:
            flash("Cannot change required quantity in shopping cart! Check quantity on sale and try again")
    return render_template('select-quantity.html', form = form)
#-------------------------------------------------------------------------------

#-----------------Route for deleting a commodity from shopping cart-------------
@main.route('/delete_cart/<id>')
@login_required
def delete_cart(id):
    comm=goodsCart.query.filter_by(id=id).first()
    if current_user.is_authenticated:
        db.session.delete(comm)
        db.session.commit()
        flash("The commodity has been deleted from the shopping cart!")
        commoditiess = goodsCart.query.filter_by(added=True).all()
        return render_template('shopping_cart.html', commodities = commoditiess)
    return render_template('shopping_cart.html', commodities = commoditiess)
    
#--------------------------------------------------------------------------------

#--------Route for paying in cash------------------------------------------------
@main.route('/cash_payment/')
@login_required
def cash_payment():
    commodities = goodsCart.query.filter_by(buyer = current_user.name).all()
    coomm1 = goodsCart.query.filter_by(buyer = current_user.name).first()
    sum = 0
    for comm4 in commodities:
        sum = sum + comm4.price
    return render_template('cash.html', sum = sum, commodities = commodities,
        coomm1=coomm1)
#--------------------------------------------------------------------------------
#----------Route for paying via MPESA--------------------------------------------
@main.route('/mpesa_payment/')
@login_required
def mpesa_payment():
    commodities = goodsCart.query.filter_by(buyer = current_user.name).all()
    coomm1 = goodsCart.query.filter_by(buyer = current_user.name).first()
    sum = 0
    for comm5 in commodities:
        sum = sum + comm5.price
    return render_template('mpesa.html', sum = sum, commodities = commodities,
        coomm1=coomm1)
#--------------------------------------------------------------------------------
#---------Route for confirming purchase of goods---------------------------------
@main.route('/confirm/')
@login_required
def confirm():
    commodities = goodsCart.query.filter_by(buyer = current_user.name).all()
    for comm6 in commodities:
        commodities2 = Commodity.query.filter_by(id=comm6.id).first()
        quan = commodities2.quantity - comm6.reqQuantity
        if quan ==0:
            change2 = Commodity(name = commodities2.name,
                type = commodities2.type,
                manDate = commodities2.manDate,
                expDate = commodities2.expDate,
                quantity = commodities2.quantity - comm6.reqQuantity,
                oldPrice = commodities2.oldPrice,
                discPrice = commodities2.discPrice,
                percDiscount = commodities2.percDiscount,
                timestamp = commodities2.timestamp,
                inStock = 'No',
                author1 = commodities2.author1)
            change3 = goodsPurchased(name = commodities2.name,
                type = commodities2.type,
                manDate = commodities2.manDate,
                expDate = commodities2.expDate,
                reqQuantity = comm6.reqQuantity,
                price = (commodities2.discPrice)*(comm6.reqQuantity),
                percDiscount = commodities2.percDiscount,
                timestamp = commodities2.timestamp,
                bought = True,
                claimed = False,
                buyer = current_user.name,
                seller = commodities2.author1)
        else:
            change2 = Commodity(name = commodities2.name,
                type = commodities2.type,
                manDate = commodities2.manDate,
                expDate = commodities2.expDate,
                quantity = commodities2.quantity - comm6.reqQuantity,
                oldPrice = commodities2.oldPrice,
                discPrice = commodities2.discPrice,
                percDiscount = commodities2.percDiscount,
                timestamp = commodities2.timestamp,
                author1 = commodities2.author1)
            change3 = goodsPurchased(name = commodities2.name,
                type = commodities2.type,
                manDate = commodities2.manDate,
                expDate = commodities2.expDate,
                reqQuantity = comm6.reqQuantity,
                price = (commodities2.discPrice)*(comm6.reqQuantity),
                percDiscount = commodities2.percDiscount,
                timestamp = commodities2.timestamp,
                bought = True,
                claimed = False,
                buyer = current_user.name,
                seller = commodities2.author1)
        db.session.add(change2)
        db.session.add(change3)
        db.session.delete(commodities2)
        db.session.delete(comm6)
        db.session.commit()
    flash("Your order has been confirmed! Please visit our office to claim your goods.")
    return render_template('catalog.html')
#-----------------------------------------------------------------------------
#---------Route for requesting to be an admin---------------------------------
@main.route('/become-admin/', methods=['GET', 'POST'])
@login_required
def become_admin():
    form = PendingForm()
    if form.validate_on_submit():
        issuess = Pending(name = current_user.name,
            username = current_user.username,
            issue = form.issue.data)
        db.session.add(issuess)
        db.session.commit()
        flash('Your request has been submitted! You will be contacted soon.')
        return render_template('index.html')
    return render_template('become_admin.html', form=form)
#----------------------------------------------------------------------------
#----------------Route for viewing requests----------------------------------
@main.route('/request/')
@login_required
def request():
    requests = Pending.query.order_by(Pending.timestamp.desc()).all()
    return render_template('requests.html', requests = requests)
#----------------------------------------------------------------------------
#---------Route for deleting a request---------------------------------------
@main.route('/delete-request/<id>', methods=['GET', 'POST'])
@login_required
def delete_request(id):
    del1=Pending.query.filter_by(id=id).first()
    db.session.delete(del1)
    db.session.commit()
    flash('The request has been deleted!')
    return redirect(url_for('.request'))
#----------------------------------------------------------------------------
#-------Route for seeing goods bought on admin side----------------------------------------
@main.route('/bought/', methods=['GET', 'POST'])
@login_required
def bought():
    bought = goodsPurchased.query.order_by(goodsPurchased.timestamp.desc()).all()
    return render_template('bought.html',bought = bought)
#----------------------------------------------------------------------------
#--------Route to confirm claim of goods--------------------------------------
@main.route('/confirm_claim/<id>', methods=['GET', 'POST'])
@login_required
def confirm_claim(id):
    good1 = goodsPurchased.query.filter_by(id=id).first()
    change4 = goodsPurchased(id = good1.id,
        name = good1.name,
        type = good1.type,
        manDate = good1.manDate,
        expDate = good1.expDate,
        reqQuantity = good1.reqQuantity,
        price = good1.price,
        percDiscount = good1.percDiscount,
        timestamp = good1.timestamp,
        bought = True,
        claimed = True,
        buyer = good1.buyer,
        seller = good1.seller)
    db.session.add(change4)
    db.session.delete(good1)
    db.session.commit()
    flash('The claim has been confirmed!')
    bought = goodsPurchased.query.order_by(goodsPurchased.timestamp.desc()).all()
    return render_template('bought.html', bought = bought)
#---------------------------------------------------------------------------------
#--------------Route for showing purchased goods-----------------------------
@main.route('/show_bought/<user>')
@login_required
def show_bought(user):
    comm12 = goodsPurchased.query.filter_by(buyer = user).all()
    sum1 = 0
    for comm in comm12:
        sum1 = sum1+comm.price
    return render_template('showbought.html', commodities = comm12, sum = sum1, user = user)
#----------------------------------------------------------------------------
#--------------Route for showing sold goods----------------------------------
@main.route('/show_sold/<user>')
@login_required
def show_sold(user):
    comm13 = goodsPurchased.query.filter_by(seller = user).all()
    sum2 = 0
    for comm in comm13:
        sum2 = sum2+comm.price
    return render_template('showsold.html', commodities = comm13, sum = sum2, user = user)
#-----------------------------------------------------------------------------
#----Route for seeing out-of-stock goods-------------------------------
@main.route('/outstock')
@login_required
def outstock():
    stock = Commodity.query.filter_by(inStock="No").all()
    return render_template('stock.html', stocks = stock)
#-----------------------------------------------------------------------------
#----Route for deleting goods out of stock------------------------------------
@main.route('/delete-stock/<id>')
@login_required
def delete_stock(id):
    del2 = Commodity.query.filter_by(id=id).first()
    del3 = Img.query.filter_by(id=id).first()
    if del2:
        db.session.delete(del2)
        if del3:
            db.session.delete(del3)
        db.session.commit()
        stock = Commodity.query.filter_by(inStock="No").all()
        flash('Out of stock commodity has been deleted!')
        return render_template('stock.html', stocks = stock)
    flash('Commodity is no longer available!')
    return render_template('stock.html', stocks = stock)
#----------------------------------------------------------------------------
#-----------------Search box-------------------------------------------------
@main.route('/search/', methods = ['GET','POST'])
@login_required
def search():
    form = SearchForm()
    if form.validate_on_submit():
        bruh = form.searched.data
        posts = Commodity.query.filter(Commodity.name.like('%'+ bruh +'%')).order_by(
            Commodity.timestamp).all()
        usersz = User.query.filter(
            User.name.like('%'+ bruh +'%')).all()
        user = User.query.filter_by(name=current_user.name).first()
        return render_template('search.html', searched = bruh,
            form=form, posts=posts, user=user, users=usersz)
    flash('No such commodity on sale!')
    return render_template('index.html')
#----------------------------------------------------------------------------
#---------Route for sending message to user-----------------------------------
@main.route('/send_message/<name>', methods = ['GET','POST'])
@login_required
def send_message(name):
    form=SendMessageForm()
    if form.validate_on_submit():
        mess = Dashboard(name = name,
            message = form.message.data)
        db.session.add(mess)
        db.session.commit()
        flash("Your message has been sent successfully!")
        requests = Pending.query.order_by(Pending.timestamp.desc()).all()
        return render_template('requests.html', requests=requests)
    return render_template('send_message.html', form=form)
#-----------------------------------------------------------------------------
#--------Route for uploading images-------------------------------------------
@main.route('/upload', methods=['GET','POST'])
@login_required
def upload():
    from flask import request
    pic = request.files['pic']
    if not pic:
        flash('No picture uploaded')
        return render_template('upload_pics.html')
    #filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    comm11 = goodsPending.query.order_by(goodsPending.timestamp.desc()).first()
    img = Img(img=pic.read(), mimetype=mimetype, commsID=comm11.id)
    db.session.add(img)
    db.session.commit()
    flash('Your image has been uploaded successfully! Upon commodity verification you will be messaged by our admins on the next step')
    return render_template('catalog.html')
#---------------------------------------------------------------------------
@main.route('/view/<id>')
@login_required
def view(id):
    img = Img.query.filter_by(id=id).order_by(Img.timestamp.desc()).first()
    if not img:
        return 'No image with that ID', 404
    return Response(img.img, mimetype=img.mimetype)
    
#---------------------------------------------------------------------------
#-----------view full picture-----------------------------------------------
@main.route('/view-all/<id>')
@login_required
def view_all(id):
    img = Img.query.filter_by(id=id).first()
    comm = Commodity.query.filter_by(id=id).first()
    if not img:
        return 'No image with that ID', 404
    return Response(img.img, mimetype=img.mimetype)
#---------------------------------------------------------------------------
#--------------------Route for general issues/requests----------------------
@main.route('/general', methods=['GET','POST'])
@login_required
def general():
    form = GeneralForm()
    if form.validate_on_submit():
        issues = Pending(name = current_user.name,
            username = current_user.username,
            issue = form.issue.data)
        db.session.add(issues)
        db.session.commit()
        flash('Your general concern has been submitted!')
        return redirect(url_for('auth.index2'))
    return render_template('genreq.html', form = form)
#---------------------------------------------------------------------------
#----------Reporting a posted commodity-------------------------------------
@main.route('/report/<id>', methods = ['GET','POST'])
@login_required
def report(id):
    form = GeneralForm()
    if form.validate_on_submit():
        issues = Pending(name = current_user.name,
            username = current_user.username,
            issue = form.issue.data)
        db.session.add(issues)
        db.session.commit()
        flash('Your report has been submitted!')
        return redirect(url_for('auth.index2'))
    flash('Please be descriptive! State the name of the seller, the commodity and the issue with the commodity.')
    return render_template('genreq.html', form = form)
#-----------------------------------------------------------------------------------------
#----------------edit profile route--------------------------------
@main.route('/edit-profile2/<id>', methods=['GET', 'POST'])
@login_required
def edit_profile2(id):
    form = EditProfileForm()
    if form.validate_on_submit():
        old = User.query.filter_by(user_id=id).first()
        new = User(name = form.name.data,
            username = form.username.data,
            email = form.email.data,
            yearOfStudy = form.yearOfStudy.data,
            regNumber = form.regNumber.data,
            phoneNumber = form.phoneNumber.data,
            password = form.password.data,
            secQuestion = form.secQuestion.data,
            secAnswer = form.secAnswer.data)
        db.session.delete(old)
        db.session.commit()
        db.session.add(new)
        db.session.commit()
        flash('Your profile has been updated! Please login.')
        return redirect(url_for('auth.login'))
    return render_template('edit_profile.html', form=form)
#--------------------------------------------------------------------------
#---------Route for rendering rules and regulations------------------------
@main.route('/rules/')
def rules():
    return render_template('rules.html')
#---------------------------------------------------------------------------
#---------Route for viewing a specific commodity----------------------------
@main.route('/comview/<id>', methods=['GET', 'POST'])
@login_required
def comview(id):
    comm78 = goodsPending.query.filter_by(id=id).first()
    comm87 = Commodity.query.filter_by(name=comm78.name).first()
    return render_template('view_comm.html', commodity=comm78, commodity2=comm87)
#---------------------------------------------------------------------------
#--------Add to Commodities list after approval-----------------------------
@main.route('/add/<time>', methods=['GET','POST'])
@login_required
def add(time):
    comm112 = goodsPending.query.filter_by(timestamp=time).first()
    commtype = comm112.type
    user3 = User.query.filter_by(name=comm112.author2).first()
    user4=user3.username
    if comm112:
        comm122 = Commodity(name = comm112.name,
            type = comm112.type,
            manDate = comm112.manDate,
            expDate = comm112.expDate,
            quantity = comm112.quantity,
            oldPrice = comm112.oldPrice,
            discPrice = comm112.discPrice,
            percDiscount = comm112.percDiscount,
            author1 = comm112.author2,
            inStock = comm112.inStock,
            addDesc = comm112.addDesc)
        if commtype == 'Foodstuffs':
            issues = Pending(name = comm112.author2,
                username = user4,
                issue = "Foodstuff added! Monitor accordingly.")
            db.session.add(issues)
            db.session.commit()
        db.session.add(comm122)
        db.session.delete(comm112)
        db.session.commit()
        flash('The commodity post has been verified!')
        return redirect(url_for('.request'))
    return render_template('index.html')
#----------------------------------------------------------------
#----------See all messages in dashboard-------------------------
@main.route('/see-all/<id>', methods = ['GET', 'POST'])
@login_required
def see_all(id):
    user = User.query.filter_by(user_id = id).first()
    mess = Dashboard.query.filter_by(name = user.name).order_by(Dashboard.timestamp.desc()).all()
    return render_template('alldash.html', messages = mess)
#----------------------------------------------------------------
#--------------Show commodity picture in pending list-----------------------
@main.route('/viewsss/<id>')
@login_required
def viewsss(id):
    img2 = Img.query.order_by(Img.timestamp.desc()).first()
    idg = img2.id
    idg2 = int(idg) - int(id)
    print(idg2)
    print(int(idg))
    print(int(id))
    img = Img.query.filter_by(id=idg).order_by(Img.timestamp.desc()).first()
    if not img:
        return 'No image with that ID', 404
    return Response(img.img, mimetype=img.mimetype)
#---------------------------------------------------------------------------
#------------Deleting a commodity from GoodsPending-------------------------
@main.route('/delpend/<id>', methods=['GET', 'POST'])
@login_required
def delpend(id):
    comm = goodsPending.query.filter_by(id=id).first()
    img1 = Img.query.filter_by(id=id).order_by(Img.id.desc()).first()
    db.session.delete(comm)
    if img1:
        db.session.delete(img1)
    db.session.commit()
    requests = Pending.query.order_by(Pending.timestamp.desc()).all()
    flash('Pending good has been deleted!')
    return render_template('requests.html', requests = requests)
#----------------------------------------------------------------------------
