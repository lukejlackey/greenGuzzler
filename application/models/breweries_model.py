from application import DATABASE
from application.models.users_model import User
from application.config.mysqlconnection import connectToMySQL
from flask import flash 

class Brewery:
    
    TABLE_NAME = 'breweries'
    OTM_TABLE_NAME = 'beers'
    MTM_TABLE_NAME = 'users_go_to_breweries'
    BEERS_MTM_TABLE_NAME = 'users_taste_beers'
    ATTR_TAGS = ['name', 'type', 'address', 'state', 'city', 'zip', 'poster_id']
    MTM_IDS = ['users_id','breweries_id']
    NAME_LENGTH = 1
    BREWERY_TYPES = ['Nano', 'Micro', 'Pub', 'Regional', 'Regional Craft', 'Large']
    
    def __init__(self, data) -> None:
        self.id = data['id']
        for tag in self.ATTR_TAGS:
            if tag is 'type':
                setattr(self, tag, self.BREWERY_TYPES[data[tag]])
            else:
                setattr(self, tag, data[tag])

    @classmethod
    def get_all_breweries(cls):
        query = f"SELECT * FROM {cls.TABLE_NAME} "
        query += f'LEFT JOIN {User.TABLE_NAME} ON {cls.TABLE_NAME}.poster_id = {User.TABLE_NAME}.id '        
        query += f'LEFT JOIN {cls.MTM_TABLE_NAME} ON {cls.TABLE_NAME}.id = {cls.MTM_TABLE_NAME}.breweries_id '
        query += f'ORDER BY {cls.TABLE_NAME}.id DESC;'
        rslt = connectToMySQL(DATABASE).query_db(query)
        if not rslt:
            return False
        breweries = [cls(brewery) for brewery in rslt]
        return breweries

    @classmethod
    def get_all_user_breweries(cls, user_id):
        query = f'SELECT {cls.TABLE_NAME}.*, COUNT({cls.MTM_TABLE_NAME}.users_id) AS subcount FROM {cls.TABLE_NAME} '
        query += f'LEFT JOIN {cls.MTM_TABLE_NAME} ON {cls.TABLE_NAME}.id = {cls.MTM_TABLE_NAME}.breweries_id '
        query += f'WHERE user_id = {user_id} '
        query += f'GROUP BY {cls.TABLE_NAME}.id; '
        rslt = connectToMySQL(DATABASE).query_db(query)
        if not rslt:
            return False
        breweries = [cls(brewery) for brewery in rslt]
        return breweries

    @classmethod
    def get_brewery(cls, id):
        query = f"SELECT {cls.TABLE_NAME}.*, {cls.OTM_TABLE_NAME}.*, poster.first_name, poster.last_name, poster.id, {cls.MTM_TABLE_NAME}.users_id AS visitors FROM {cls.TABLE_NAME} "
        query += f"LEFT JOIN {User.TABLE_NAME} AS poster ON {cls.TABLE_NAME}.poster_id = poster.id "
        query += f'LEFT JOIN {cls.MTM_TABLE_NAME} ON {cls.TABLE_NAME}.id = {cls.MTM_TABLE_NAME}.breweries_id '
        query += f'LEFT JOIN {User.TABLE_NAME} ON {cls.MTM_TABLE_NAME}.users_id = {User.TABLE_NAME}.id '
        query += f'LEFT JOIN {cls.BEERS_MTM_TABLE_NAME} ON {cls.OTM_TABLE_NAME}.id = {cls.BEERS_MTM_TABLE_NAME}.beers_id '
        query += f'WHERE {cls.TABLE_NAME}.id = {id};'
        rslt = connectToMySQL(DATABASE).query_db(query)
        print(rslt)
        return cls(rslt[0]) if rslt else False

    @classmethod
    def validate_create_brewery(cls, brewery_info):
        info_dict = {
            'name' : 
                (f'Your brewery name must be at least {cls.NAME_LENGTH} characters long.', 
                'error_create_brewery_name',
                len(brewery_info['name']) >= cls.NAME_LENGTH)
        }
        return cls.validate_data(brewery_info, info_dict)

    @classmethod
    def create_new_brewery(cls, brewery_info):
        query = f"INSERT INTO {cls.TABLE_NAME}( {', '.join(cls.ATTR_TAGS)} ) "
        cols = []
        for tag in cls.ATTR_TAGS:
            cols.append( f'%({tag})s' )
        cols = ', '.join(cols)
        query += f'VALUES( {cols} );'
        rslt = connectToMySQL(DATABASE).query_db(query, brewery_info)
        return rslt

    @classmethod
    def update_brewery(cls, new_info):
        query = f'UPDATE {cls.TABLE_NAME} '
        cols = []
        for tag in cls.ATTR_TAGS:
            cols.append( f'{tag} = %({tag})s' )
        cols = ', '.join(cols)
        query += f'SET {cols} '
        query += 'WHERE id = %(id)s;'
        print(query)
        rslt = connectToMySQL(DATABASE).query_db(query, new_info)
        return rslt

    @classmethod
    def delete_brewery(cls, id):
        query = f'SELECT * FROM {cls.MTM_TABLE_NAME} WHERE breweries_id = {id};'
        if connectToMySQL(DATABASE).query_db(query):
            query = f'DELETE {cls.MTM_TABLE_NAME}, {cls.TABLE_NAME} FROM {cls.MTM_TABLE_NAME} '
            query += f'LEFT JOIN {cls.TABLE_NAME} ON {cls.MTM_TABLE_NAME}.breweries_id = {cls.TABLE_NAME}.id '
        else:
            query = f'DELETE {cls.TABLE_NAME}, {cls.MTM_TABLE_NAME} FROM {cls.TABLE_NAME} '
            query += f'LEFT JOIN {cls.MTM_TABLE_NAME} ON {cls.TABLE_NAME}.id = {cls.MTM_TABLE_NAME}.breweries_id '
        query += f'WHERE id = {id};'
        rslt = connectToMySQL(DATABASE).query_db(query)
        return rslt

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