import logging
import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
logging.debug('Starting app...')

UPLOAD_FOLDER = 'application/static/img/avatars'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATABASE = os.environ.get("DATABASE")