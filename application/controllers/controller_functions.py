from application import ALLOWED_EXTENSIONS
from application.models.users_model import User
from flask import session

def check_user():
    return User.get_user(id=session['logged_user']) if 'logged_user' in session else False

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS