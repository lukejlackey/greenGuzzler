import os
from application import app
from application.models.beers_model import Beer
from application.models.breweries_model import Brewery
from application.models.users_model import User
from application.models.quote_model import Quote
from flask import render_template, redirect, request, session, flash
from application.controllers.controller_functions import check_user, allowed_file
from werkzeug.utils import secure_filename

@app.route('/', methods=['GET'])
def home():
    user = check_user()
    all_breweries = Brewery.get_all_breweries()
    all_beers = Beer.get_all_beers()
    return render_template('index.html', user=user, breweries=all_breweries, beers=all_beers)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if check_user():
        return redirect('/')
    if request.method == 'GET':
        return render_template('login.html', quote=Quote())
    elif request.method == 'POST':
        if 'first_name' in request.form:
            new_user = User.create_new_user(request.form)
            if new_user:
                session['logged_user'] = new_user.id
                return redirect(f'/users/{new_user.id}/dash')
        else:
            user = User.validate_login(request.form)
            if not user:
                flash('Invalid credentials', 'error_login_inv_creds')
                return redirect('/login')
            session['logged_user'] = user.id
            return redirect('/')
        return redirect('/login')

@app.route('/users/<int:id>/dash', methods=['GET'])
def dash(id):
    current_user = check_user()
    if not current_user:
        return redirect('/login')
    if id != current_user.id:
        return redirect('/')
    posted_breweries = Brewery.get_all_user_breweries(id)
    posted_beers = Beer.get_all_user_beers(id)
    visited_breweries = Brewery.get_all_visited_breweries(id)
    rated_beers = Beer.get_all_rated_beers(id)
    return render_template('dash.html', user=current_user, posted_breweries=posted_breweries, posted_beers=posted_beers, visited_breweries=visited_breweries, rated_beers=rated_beers)
    
@app.route('/users/<int:id>/account', methods=['GET', 'POST'])
def account(id):
    current_user = check_user()
    if not current_user:
        return redirect('/login')
    if id != current_user.id:
        return redirect('/')
    if request.method == 'GET':
        return render_template('account.html', user=current_user)
    elif request.method == 'POST':
        if 'first_name' in request.form:
            updated_user = User.edit_user(request.form, id)
        else:
            if 'avatar' not in request.files:
                flash('No file part', 'error_avatar_msg')
                return redirect(f'/users/{id}/account')
            file = request.files['avatar']
            if file.filename == '':
                flash('No selected file', 'error_avatar_msg')
                return redirect(f'/users/{id}/account')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'{id}-{filename}')
                file.save(filepath)
                User.edit_avatar(f"'{id}-{filename}'", id)
        return redirect(f'/users/{id}/account')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')