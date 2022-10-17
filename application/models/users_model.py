from application import app, DATABASE
from application.config.mysqlconnection import connectToMySQL
from application.models.model_functions import validate_data
from flask import flash
from flask_bcrypt import Bcrypt
import re
bcrypt = Bcrypt(app)

class User:
    
    # MySQL
    TABLE_NAME = 'users'
    
    # User attributes
    ATTR_TAGS = ['first_name','last_name','email','password', 'avatar']
    DEFAULT_AVATAR = 'default.png'
    
    # Validation params
    FIRST_NAME_LENGTH = 2
    LAST_NAME_LENGTH = 2
    PASSWORD_LENGTH = 8
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
    PASSWORD_REGEX = re.compile(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])')
    
    # Constructor
    def __init__(self, data) -> None:
        self.id = data['id']
        for tag in self.ATTR_TAGS:
            setattr(self, tag, data[tag])
        if 'avatar' in data:
            self.avatar = data['avatar']

    # Retrieve a user
    @classmethod
    def get_user(cls, user_data=None, id=False):
        query = f'SELECT * FROM {cls.TABLE_NAME} WHERE '
        query += 'email = %(email)s;' if not id else f'id = {id};'
        rslt = connectToMySQL(DATABASE).query_db(query, user_data)
        return cls(rslt[0]) if rslt else False

    # Validate login attempt
    @classmethod
    def validate_login(cls, credentials):
        validations = {
            'email' : {
                'tag' : 'error_login_email',
                'msg' : 'Please provide your email.',
                'condition' : None
            },
            'password' : {
                'tag' : 'error_login_pw',
                'msg' : 'Please enter your password.',
                'condition' : None
            }
        }
        if not validate_data(credentials, validations):
            return False
        current_user = cls.get_user(user_data=credentials)
        if not current_user or not bcrypt.check_password_hash(current_user.password, credentials['password']):
            return False
        return current_user

    # Validate registration attempt
    @classmethod
    def validate_registration(cls, user_info):
        validations = {
            'first_name' : {
                'tag' : 'error_reg_fn',
                'msg' : f'Your first name must be at least {cls.FIRST_NAME_LENGTH} characters long.',
                'condition' : len(user_info['first_name']) >= cls.FIRST_NAME_LENGTH
            },
            'last_name' : {
                'tag' : 'error_reg_ln',
                'msg' : f'Your last name must be at least {cls.LAST_NAME_LENGTH} characters long.',
                'condition' : len(user_info['last_name']) >= cls.LAST_NAME_LENGTH
            },
            'email' : {
                'tag' : 'error_reg_email',
                'msg' : 'Please provide a valid email.',
                'condition' : cls.EMAIL_REGEX.match(user_info['email']) != None
            },
            'password' : {
                'tag' : 'error_reg_pw',
                'msg' : f'Your password must include: at least {cls.PASSWORD_LENGTH} characters, an upper case letter, a lower case letter, a number, and a special character.',
                'condition' : len(user_info['password']) >= cls.PASSWORD_LENGTH and cls.PASSWORD_REGEX.match(user_info['password']) != None
            },
            'confirm_pw' : {
                'tag' : 'error_reg_conf_pw',
                'msg' : 'Passwords must match.',
                'condition' : user_info['password'] == user_info['confirm_pw']
            }
        }
        validity = validate_data(user_info, validations)
        if 'email' in user_info:
            query = f'SELECT * FROM {cls.TABLE_NAME} '
            query += 'WHERE email = %(email)s;'
            rslt = connectToMySQL(DATABASE).query_db(query, user_info)
            if rslt:
                flash('An account with this email has already been registered. Please try another.',
                    'error_reg_email')
                validity = False
        return validity

    # Create new user row in MySQL DB
    @classmethod
    def create_new_user(cls, user_info):
        valid_info = cls.validate_registration(user_info)
        if not valid_info:
            return False
        new_user_data = {
            **user_info,
            'password': bcrypt.generate_password_hash(user_info['password']),
            'avatar': cls.DEFAULT_AVATAR
        }
        query = f"INSERT INTO {cls.TABLE_NAME}( {', '.join(cls.ATTR_TAGS)} ) "
        cols = ', '.join([f'%({tag})s' for tag in cls.ATTR_TAGS])
        query += f'VALUES( {cols} );'
        new_user_data['id'] = connectToMySQL(DATABASE).query_db(query, new_user_data)
        new_user = cls(new_user_data)
        return new_user

    # Edit existing user
    @classmethod
    def edit_user(cls, new_info, id):
        validations = {
            'first_name' : {
                'tag' : 'error_reg_fn',
                'msg' : f'Your first name must be at least {cls.FIRST_NAME_LENGTH} characters long.',
                'condition' : len(new_info['first_name']) >= cls.FIRST_NAME_LENGTH
            },
            'last_name' : {
                'tag' : 'error_reg_ln',
                'msg' : f'Your last name must be at least {cls.LAST_NAME_LENGTH} characters long.',
                'condition' : len(new_info['last_name']) >= cls.LAST_NAME_LENGTH
            },
            'email' : {
                'tag' : 'error_reg_email',
                'msg' : 'Please provide a valid email.',
                'condition' : cls.EMAIL_REGEX.match(new_info['email']) != None
            }
        }
        if not validate_data(new_info, validations):
            return False
        current_user = cls.get_user(id=id)
        if current_user and current_user.email != new_info['email']:
            query = f'SELECT * FROM {cls.TABLE_NAME} '
            query += 'WHERE email = %(email)s;'
            rslt = connectToMySQL(DATABASE).query_db(query, new_info)
            if rslt:
                flash('An account with this email has already been registered. Please try another.',
                    'error_update_email')
                return False
        query = f'UPDATE {cls.TABLE_NAME} '
        cols = []
        for tag in validations.keys():
            cols.append( f'{tag} = %({tag})s' )
        cols = ', '.join(cols)
        query += f'SET {cols} '
        query += f'WHERE id = {id};'
        rslt = connectToMySQL(DATABASE).query_db(query, new_info)

    #Edit avatar picture
    @classmethod
    def edit_avatar(cls, filepath, id):
        query = f'UPDATE {cls.TABLE_NAME} '
        query += f'SET avatar = {filepath} '
        query += f'WHERE id = {id};'
        rslt = connectToMySQL(DATABASE).query_db(query)