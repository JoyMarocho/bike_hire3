from pickle import GET
from flask import abort, render_template
from flask import render_template,request,redirect,url_for
from flask_login import login_required,current_user
from ..models import Bikes, User, Reviews, Hired_Bikes
from . import main
from .. import db,photos
from .forms import ReviewForm, UpdateProfile, BikeForm
from werkzeug.utils import secure_filename
import os
from app import create_app

app = create_app('development')

@main.route('/')
def index():

    '''
    View root page function that returns the index page and its data
    '''
   
    title = 'Bike Hire'
    return render_template('index.html',  title = title)

@main.route('/user')
@login_required
def user():
    username = current_user.username
    user = User.query.filter_by(username=username).first()
    if user is None:
        return ('not found')
    return render_template('profile.html', user=user)


@main.route('/user/<username>')
def profile(username):
    user = User.query.filter_by(username = username).first()

    if user is None:
        abort(404)

    return render_template("profile/profile.html", user = user)


@main.route('/user/<username>/update',methods = ['GET','POST'])
@login_required
def update_profile(username):
    user = User.query.filter_by(username = username).first()
    if user is None:
        abort(404)

    form = UpdateProfile()

    if form.validate_on_submit():
        user.bio = form.bio.data

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('.profile',username=user.username))

    return render_template('profile/updates.html',update_form =form)

@main.route('/user/<username>/update/pic',methods= ['POST'])
@login_required
def update_pic(username):
    user = User.query.filter_by(username = username).first()
    if 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        path = f'photos/{filename}'
        user.profile_pic_path = path
        db.session.commit()
    return redirect(url_for('main.profile',username=username))

@main.route('/reviews/<bikes_id>',methods= ['POST','GET'])
@login_required
def review(bikes_id):
    '''
    function to return the reviews
    '''
    form = ReviewForm()
    bike = Bikes.query.get(bikes_id)
    user = User.query.all()
    reviews = Reviews.query.filter_by(bikes_id=bikes_id).all()
    if form.validate_on_submit():
        review = form.review.data
        bikes_id = bikes_id
        user_id = current_user._get_current_object().id
        new_review = Reviews(
            review=review,
            bikes_id=bikes_id,
            user_id=user_id,
            )

        db.session.add(new_review)
        db.session.commit()
        
        new_reviews = [new_review]
        print(new_reviews)
        return redirect(url_for('.review', bikes_id=bikes_id))
    return render_template('reviews.html', form=form, bike=bike, reviews=reviews, user=user)

@main.route('/bikes')
@login_required
def bikes():
    bikes = Bikes.query.filter_by(hired=False).all()
    
    return render_template('bikes_display.html', bikes=bikes)

@main.route('/new_bike', methods=['GET', 'POST'])
@login_required
def new_bike():

    '''
    View bike page function that returns the bike details page and its data
    '''
    title = 'Bike Hire'
    

    form = BikeForm()
    if form.validate_on_submit():
        pic = request.files['image']
        pic_name = secure_filename(pic.filename)
        # pic.save(os.path.join(app.config['UPLOAD_FOLDER'],pic_name))
        path = os.path.join(app.root_path,'static/uploads',pic.filename)
        pic.save(path)
        category= form.category.data
        
        user_id = current_user._get_current_object().id
        bikes_obj = Bikes(user_id=user_id,category=category,bike_pic_path=pic_name)
        # bikes_obj.save_bike
        
        db.session.add(bikes_obj)
        db.session.commit()
        
        return redirect(url_for('main.bikes'))
    return render_template('new_bike.html', bike_form=form)


@main.route('/hire/<bikes_id>',methods=['GET', 'POST'])
@login_required
def hire(bikes_id):
    hired_bike=Bikes.query.filter_by(id=int(bikes_id)).first()
    hired_bike.hired=True
    
    hire_bike=Hired_Bikes(user_id=current_user.id,bike_id=int(bikes_id))
    
    db.session.add(hire_bike)
    db.session.commit()
    
    db.session.add(hired_bike)
    db.session.commit()
    
    return redirect (url_for('main.bikes'))
    
@main.route('/view_hired/',methods=['GET'])
@login_required
def view_hired():
    bikes = Hired_Bikes.query.filter_by(user_id=current_user.id).all()
    
  
    return render_template('hired.html',bikes=bikes)


@main.route('/returnbike/<bike_id>',methods=['GET', 'POST'])
@login_required
def returnbike(bike_id):
    hired_bike=Bikes.query.filter_by(id=int(bike_id)).first()
    hired_bike.hired=False
    
    db.session.add(hired_bike)
    db.session.commit()
    
    Hired_Bikes.query.filter_by(bike_id=int(bike_id)).delete()
    db.session.commit()
    
    return redirect(url_for('main.view_hired'))

@main.route('/about',methods=['GET', 'POST'])
def about():
    
    return render_template('about.html')

@main.route('/contacts',methods=['GET', 'POST'])
def contacts():
    
    return render_template('contacts.html')
