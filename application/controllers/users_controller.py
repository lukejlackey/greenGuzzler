from application import app, ALLOWED_EXTENSIONS
import os
from application.models.beers_model import Beer
from application.models.breweries_model import Brewery
from application.models.users_model import User
from application.models.quote_model import Quote
from flask import render_template, redirect, request, session, flash
from werkzeug.utils import secure_filename

def invalid_creds():
    flash('Invalid credentials', 'error_login_inv_creds')
    return redirect('/login')

def check_user():
    return User.get_user(id=session['logged_user']) if 'logged_user' in session else False

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def home():
    user = check_user()
    all_breweries = Brewery.get_all_breweries()
    all_beers = Beer.get_all_beers()
    return render_template('index.html', user=user, breweries=all_breweries, beers=all_beers)

@app.route('/users/<int:id>/dashboard')
def show_dashboard(id):
    if 'logged_user' not in session:
        return redirect('/')
    if id != session['logged_user']:
        return redirect('/')
    current_user = User.get_user(id=id)
    all_items = Brewery.get_all_breweries()
    return render_template('dashboard.html', user=current_user, items=all_items)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if check_user():
        return redirect('/')
    if request.method == 'GET':
        return render_template('login.html', quote=Quote())
    elif request.method == 'POST':
        if 'first_name' in request.form:
            if User.validate_register(request.form):
                new_user = User.register_new_user(dict(request.form))
                if new_user:
                    session['logged_user'] = new_user.id
                    return redirect(f'/users/{new_user.id}/dashboard')
        else:
            user = User.validate_login(request.form)
            if not user:
                return invalid_creds()
            session['logged_user'] = user.id
            return redirect('/')
    return redirect('/login')

@app.route('/users/<int:id>/account', methods=['GET', 'PUT'])
def account(id):
    current_user = check_user()
    if not current_user:
        return redirect('/login')
    if id != current_user.id:
        return redirect('/')
    if request.method == 'GET':
        return render_template('account.html', user=current_user)
    elif request.method == 'POST':
        if 'avatar' in request.form:
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
        else:
            updated_user = User.edit_user(request.form, id)
        return redirect(f'/users/{id}/account')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')