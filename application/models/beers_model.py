from application import DATABASE
from application.models.users_model import User
from application.config.mysqlconnection import connectToMySQL
from flask import flash 

class Beer:
    
    TABLE_NAME = 'beers'
    MTM_TABLE_NAME = 'users_taste_beers'
    ATTR_TAGS = ['name', 'type', 'abv', 'breweries_id', 'poster_id']
    MTM_TAGS = ['users_id', 'beers_id', 'taste', 'cost', 'val']
    NAME_LENGTH = 1
    TYPE_LENGTH = 3
    ABV_MIN = 0
    ABV_MAX = 100
    BEER_TYPES = ['Nano', 'Micro', 'Pub', 'Regional', 'Regional Craft', 'Large']
    
    def __init__(self, data) -> None:
        self.id = data['id']
        for tag in self.ATTR_TAGS:
            if tag == 'abv':
                setattr(self, tag, float(data[tag]))
            else:
                setattr(self, tag, data[tag])
        if 'brewery' in data:
            setattr(self, 'brewery', data['brewery'])
        if 'poster_first_name' in data:
            setattr(self, 'poster_first_name', data['poster_first_name'])
        if 'poster_last_name' in data:
            setattr(self, 'poster_last_name', data['poster_last_name'])
        if 'poster_avatar' in data:
            setattr(self, 'poster_avatar', data['poster_avatar'])
        if 'tasters' in data:
            setattr(self, 'tasters', data['tasters'])
        if 'taste' in data:
            setattr(self, 'taste', round(data['taste']))
        if 'cost' in data:
            setattr(self, 'cost', round(data['cost']))
        if 'val' in data:
            setattr(self, 'val', round(data['val']))

    @classmethod
    def get_all_beers(cls):
        query = f"SELECT {cls.TABLE_NAME}.*, breweries.name as brewery, AVG(taste) AS taste, AVG(cost) AS cost, AVG(val) AS val FROM {cls.TABLE_NAME} "      
        query += f'LEFT JOIN breweries ON {cls.TABLE_NAME}.breweries_id = breweries.id '
        query += f'LEFT JOIN {cls.MTM_TABLE_NAME} ON {cls.TABLE_NAME}.id = {cls.MTM_TABLE_NAME}.beers_id '
        query += f'GROUP BY {cls.TABLE_NAME}.id '
        query += f'ORDER BY {cls.TABLE_NAME}.id DESC;'
        rslt = connectToMySQL(DATABASE).query_db(query)
        if not rslt:
            return False
        beers = [cls(beer) for beer in rslt]
        return beers

    @classmethod
    def get_all_beers_by_brewery(cls, brewery_id):
        query = f"SELECT {cls.TABLE_NAME}.*, breweries.name as brewery, AVG(taste) AS taste, AVG(cost) AS cost, AVG(val) AS val FROM {cls.TABLE_NAME} "      
        query += f'LEFT JOIN breweries ON {cls.TABLE_NAME}.breweries_id = breweries.id '
        query += f'LEFT JOIN {cls.MTM_TABLE_NAME} ON {cls.TABLE_NAME}.id = {cls.MTM_TABLE_NAME}.beers_id '
        query += f'WHERE breweries_id = {brewery_id} '
        query += f'GROUP BY {cls.TABLE_NAME}.id '
        query += f'ORDER BY {cls.TABLE_NAME}.id DESC;'
        rslt = connectToMySQL(DATABASE).query_db(query)
        if not rslt:
            return False
        beers = [cls(beer) for beer in rslt]
        return beers

    @classmethod
    def get_all_user_beers(cls, user_id):
        query = f'SELECT {cls.TABLE_NAME}.*, COUNT({cls.MTM_TABLE_NAME}.users_id) AS subcount FROM {cls.TABLE_NAME} '
        query += f'LEFT JOIN {cls.MTM_TABLE_NAME} ON {cls.TABLE_NAME}.id = {cls.MTM_TABLE_NAME}.beers_id '
        query += f'WHERE user_id = {user_id} '
        query += f'GROUP BY {cls.TABLE_NAME}.id; '
        rslt = connectToMySQL(DATABASE).query_db(query)
        if not rslt:
            return False
        beers = [cls(beer) for beer in rslt]
        return beers

    @classmethod
    def get_beer(cls, id):
        query = f"SELECT {cls.TABLE_NAME}.*, breweries.id AS brewery_id, breweries.name AS brewery, poster.first_name AS poster_first_name, poster.last_name AS poster_last_name, poster.avatar AS poster_avatar, COUNT({cls.MTM_TABLE_NAME}.users_id) AS tasters, AVG(taste) AS taste, AVG(cost) AS cost, AVG(val) AS val FROM {cls.TABLE_NAME} "
        query += f'LEFT JOIN breweries ON {cls.TABLE_NAME}.breweries_id = breweries.id '
        query += f"LEFT JOIN {User.TABLE_NAME} AS poster ON {cls.TABLE_NAME}.poster_id = poster.id "
        query += f'LEFT JOIN {cls.MTM_TABLE_NAME} ON {cls.TABLE_NAME}.id = {cls.MTM_TABLE_NAME}.beers_id '
        query += f'WHERE {cls.TABLE_NAME}.id = {id};'
        rslt = connectToMySQL(DATABASE).query_db(query)
        return cls(rslt[0]) if rslt else False

    @classmethod
    def validate_create_beer(cls, beer_info):
        info_dict = {
            'name' : 
                (f'Your beer name must be at least {cls.NAME_LENGTH} characters long.', 
                'error_create_beer_name',
                len(beer_info['name']) >= cls.NAME_LENGTH),
            'type' : 
                (f'Your beer type must be at least {cls.NAME_LENGTH} characters long.', 
                'error_create_beer_type',
                len(beer_info['type']) >= cls.TYPE_LENGTH),
            'abv' : 
                (f'Your beer abv must be between {cls.ABV_MIN} and {cls.ABV_MAX} %.', 
                'error_create_beer_abv',
                cls.ABV_MIN <= float(beer_info['abv'] if beer_info['abv'] else -1) < cls.ABV_MAX)
        }
        return cls.validate_data(beer_info, info_dict)

    @classmethod
    def create_new_beer(cls, beer_info):
        query = f"INSERT INTO {cls.TABLE_NAME}( {', '.join(cls.ATTR_TAGS)} ) "
        cols = []
        for tag in cls.ATTR_TAGS:
            cols.append( f'%({tag})s' )
        cols = ', '.join(cols)
        query += f'VALUES( {cols} );'
        rslt = connectToMySQL(DATABASE).query_db(query, beer_info)
        return rslt

    @classmethod
    def rate_beer(cls, rating_info):
        query = f"INSERT INTO {cls.MTM_TABLE_NAME}( {', '.join(cls.MTM_TAGS)} ) "
        cols = []
        for tag in cls.MTM_TAGS:
            cols.append( f'%({tag})s' )
        cols = ', '.join(cols)
        query += f'VALUES( {cols} ) '
        query += "ON DUPLICATE KEY UPDATE "
        for tag in cls.MTM_TAGS:
            if tag is not 'users_id' or tag is not 'beers_id':
                query += f"{tag} = {rating_info[tag]}{',' if tag is not 'val' else ';'} "
        rslt = connectToMySQL(DATABASE).query_db(query, rating_info)
        return rslt

    @classmethod
    def update_beer(cls, new_info):
        query = f'UPDATE {cls.TABLE_NAME} '
        cols = []
        for tag in cls.ATTR_TAGS:
            cols.append( f'{tag} = %({tag})s' )
        cols = ', '.join(cols)
        query += f'SET {cols} '
        query += 'WHERE id = %(id)s;'
        rslt = connectToMySQL(DATABASE).query_db(query, new_info)
        return rslt

    @classmethod
    def delete_beer(cls, id):
        query = f'SELECT * FROM {cls.MTM_TABLE_NAME} WHERE beers_id = {id};'
        if connectToMySQL(DATABASE).query_db(query):
            query = f'DELETE {cls.MTM_TABLE_NAME}, {cls.TABLE_NAME} FROM {cls.MTM_TABLE_NAME} '
            query += f'LEFT JOIN {cls.TABLE_NAME} ON {cls.MTM_TABLE_NAME}.beers_id = {cls.TABLE_NAME}.id '
        else:
            query = f'DELETE {cls.TABLE_NAME}, {cls.MTM_TABLE_NAME} FROM {cls.TABLE_NAME} '
            query += f'LEFT JOIN {cls.MTM_TABLE_NAME} ON {cls.TABLE_NAME}.id = {cls.MTM_TABLE_NAME}.beers_id '
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