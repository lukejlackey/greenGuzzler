import logging
from application import app, DATABASE
from application.config.mysqlconnection import connectToMySQL
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

    # Validate input data and return any error messages
    @staticmethod
    def validate_data(data, validations):
        validity = True
        for (k, v) in validations.items():
            if not data[k]:
                flash('This field is required.', v[1])
                validity = False
            elif not all(v):
                flash(v[0], v[1])
                validity = False
        return validity

    # Validate login attempt
    @classmethod
    def validate_login(cls, creds):
        login_validations = {
            'email' : ('Please provide your email.', 'error_login_email'),
            'password' : ('Please enter your password.', 'error_login_pw')
            }
        if not cls.validate_data(creds, login_validations):
            return False
        current_user = cls.get_user(creds)
        if not current_user or not bcrypt.check_password_hash(current_user.password, creds['password']):
            return False
        return current_user

    # Validate registration attempt
    @classmethod
    def validate_register(cls, reg_info):
        reg_validations = {
            'first_name' : 
                (f'Your first name must be at least {cls.FIRST_NAME_LENGTH} characters long.', 
                 'error_reg_fn',
                 len(reg_info['first_name']) >= cls.FIRST_NAME_LENGTH),
            'last_name' : 
                (f'Your first name must be at least {cls.LAST_NAME_LENGTH} characters long.', 
                 'error_reg_ln',
                 len(reg_info['first_name']) >= cls.LAST_NAME_LENGTH),
            'email' : 
                ('Please provide a valid email.', 
                 'error_reg_email',
                 cls.EMAIL_REGEX.match(reg_info['email']) != None),
            'password' : 
                (f'Your password must include: at least {cls.PASSWORD_LENGTH} characters, an upper case letter, a lower case letter, a number, and a special character.', 
                 'error_reg_pw',
                 len(reg_info['password']) >= cls.PASSWORD_LENGTH,
                 cls.PASSWORD_REGEX.match(reg_info['password']) != None),
            'confirm_pw' : 
                ('Passwords must match.', 
                 'error_reg_conf_pw',
                 reg_info['password'] == reg_info['confirm_pw'])
        }
        return cls.validate_data(reg_info, reg_validations)

    # Create new user row in MySQL DB
    @classmethod
    def create_new_user(cls, user_info):
        user_data = {
            **user_info,
            'password': bcrypt.generate_password_hash(user_info['password'])
        }
        query = f"INSERT INTO {cls.TABLE_NAME}( {', '.join(cls.ATTR_TAGS)} ) "
        cols = []
        for tag in cls.ATTR_TAGS:
            cols.append( f'%({tag})s' )
        cols = ', '.join(cols)
        query += f'VALUES( {cols} );'
        user_info['id'] = connectToMySQL(DATABASE).query_db(query, user_data)
        new_user = cls(user_info)
        return new_user
    
    # Register new user utilizing validateUser + createNewUser methods
    @classmethod
    def register_new_user(cls, regist_info):
        query = f'SELECT * FROM {cls.TABLE_NAME} '
        query += 'WHERE email = %(email)s;'
        rslt = connectToMySQL(DATABASE).query_db(query, regist_info)
        if rslt:
            flash('An account with this email has already been registered. Please try another.',
                  'error_reg_email')
            return False
        return cls.create_new_user({**regist_info,'avatar': cls.DEFAULT_AVATAR})

    # Edit existing user
    @classmethod
    def edit_user(cls, new_info, id):
        edit_validations = {
            'first_name' : 
                (f'Your first name must be at least {cls.FIRST_NAME_LENGTH} characters long.', 
                 'error_update_fn',
                 len(new_info['first_name']) >= cls.FIRST_NAME_LENGTH),
            'last_name' : 
                (f'Your last name must be at least {cls.LAST_NAME_LENGTH} characters long.', 
                 'error_update_ln',
                 len(new_info['last_name']) >= cls.LAST_NAME_LENGTH),
            'email' : 
                ('Please provide a valid email.', 
                 'error_update_email',
                 cls.EMAIL_REGEX.match(new_info['email']) != None)
        }
        if not cls.validate_data(new_info, edit_validations):
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
        for tag in edit_validations.keys():
            cols.append( f'{tag} = %({tag})s' )
        cols = ', '.join(cols)
        query += f'SET {cols} '
        query += f'WHERE id = {id};'
        rslt = connectToMySQL(DATABASE).query_db(query, new_info)

    #Add or edit avatar picture filename
    @classmethod
    def edit_avatar(cls, filepath, id):
        query = f'UPDATE {cls.TABLE_NAME} '
        query += f'SET avatar = {filepath} '
        query += f'WHERE id = {id};'
        rslt = connectToMySQL(DATABASE).query_db(query)