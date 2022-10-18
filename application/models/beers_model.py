from application import DATABASE
from application.models.users_model import User
from application.config.mysqlconnection import connectToMySQL
from application.models.model_functions import validate_data

class Beer:
    
    TABLE_NAME = 'beers'
    MTO_TABLE_NAME = 'breweries'
    MTM_TABLE_NAME = 'users_taste_beers'
    COLUMN_NAMES = ['name', 'type', 'abv', 'breweries_id', 'poster_id']
    MTM_COLUMN_NAMES = ['users_id', 'beers_id', 'taste', 'cost', 'val']
    BASIC_CONSTRUCTOR_ATTRS = ['id', 'name', 'type', 'breweries_id', 'brewery', 'poster_id', 'poster_first_name','poster_last_name','poster_avatar', 'tasters']
    ROUND_CONTRUCTOR_ATTRS = ['taste', 'cost', 'val']
    FLOAT_CONSTRUCTOR_ATTRS = ['abv']
    NAME_LENGTH = 1
    TYPE_LENGTH = 3
    ABV_MIN = 0
    ABV_MAX = 100
    BEER_TYPES = ['Nano', 'Micro', 'Pub', 'Regional', 'Regional Craft', 'Large']
    
    def __init__(self, data):
        for (k, v) in data.items():
            if k in self.BASIC_CONSTRUCTOR_ATTRS:
                setattr(self, k, v)
            elif k in self.ROUND_CONTRUCTOR_ATTRS:
                setattr(self, k, round(v))
            elif k in self.FLOAT_CONSTRUCTOR_ATTRS:
                setattr(self, k, float(v))

    @classmethod
    def get_all_beers(cls, sort_by=None, desc=True):
        query = f"SELECT {cls.TABLE_NAME}.*, breweries.name as brewery, AVG(taste) AS taste, AVG(cost) AS cost, AVG(val) AS val FROM {cls.TABLE_NAME} "      
        query += f'LEFT JOIN breweries ON {cls.TABLE_NAME}.breweries_id = breweries.id '
        query += f'LEFT JOIN {cls.MTM_TABLE_NAME} ON {cls.TABLE_NAME}.id = {cls.MTM_TABLE_NAME}.beers_id '
        query += f'GROUP BY {cls.TABLE_NAME}.id '
        query += f"ORDER BY {f'{cls.TABLE_NAME}.id' if sort_by is None else sort_by} {'DESC' if desc else ''};"
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
        query = f'SELECT {cls.TABLE_NAME}.* FROM {cls.TABLE_NAME} '
        query += f'WHERE poster_id = {user_id};'
        rslt = connectToMySQL(DATABASE).query_db(query)
        if not rslt:
            return False
        beers = [cls(beer) for beer in rslt]
        return beers

    @classmethod
    def get_beer(cls, id):
        query = f"SELECT {cls.TABLE_NAME}.*, {cls.MTO_TABLE_NAME}.id AS brewery_id, {cls.MTO_TABLE_NAME}.name AS brewery, poster.id AS poster_id, poster.first_name AS poster_first_name, poster.last_name AS poster_last_name, poster.avatar AS poster_avatar, COUNT({cls.MTM_TABLE_NAME}.users_id) AS tasters, AVG(taste) AS taste, AVG(cost) AS cost, AVG(val) AS val FROM {cls.TABLE_NAME} "
        query += f'LEFT JOIN {cls.MTO_TABLE_NAME} ON {cls.TABLE_NAME}.breweries_id = {cls.MTO_TABLE_NAME}.id '
        query += f"LEFT JOIN {User.TABLE_NAME} AS poster ON {cls.TABLE_NAME}.poster_id = poster.id "
        query += f'LEFT JOIN {cls.MTM_TABLE_NAME} ON {cls.TABLE_NAME}.id = {cls.MTM_TABLE_NAME}.beers_id '
        query += f'WHERE {cls.TABLE_NAME}.id = {id};'
        rslt = connectToMySQL(DATABASE).query_db(query)
        if not rslt:
            return False
        beer = cls(rslt[0])
        return beer

    @classmethod
    def validate_new_beer(cls, beer_info):
        validations = {
            'name' : {
                'tag' : 'error_create_beer_name',
                'msg' : f'Your beer name must be at least {cls.NAME_LENGTH} characters long.',
                'condition' : len(beer_info['name']) >= cls.NAME_LENGTH
            },
            'type' : {
                'tag' : 'error_create_beer_type',
                'msg' : f'Your beer type must be at least {cls.NAME_LENGTH} characters long.',
                'condition' : len(beer_info['name']) >= cls.NAME_LENGTH
            },
            'abv' : {
                'tag' : 'error_create_beer_abv',
                'msg' : f'Your beer abv must be between {cls.ABV_MIN} and {cls.ABV_MAX} %.',
                'condition' : cls.ABV_MIN <= float(beer_info['abv'] if beer_info['abv'] else cls.ABV_MIN - 1) < cls.ABV_MAX
            }
        }
        validity = validate_data(beer_info, validations)
        return validity

    @classmethod
    def create_new_beer(cls, beer_info):
        valid_info = cls.validate_new_beer(beer_info)
        if not valid_info:
            return False
        query = f"INSERT INTO {cls.TABLE_NAME}( {', '.join(cls.COLUMN_NAMES)} ) "
        cols = ', '.join([f'%({tag})s' for tag in cls.COLUMN_NAMES])
        query += f'VALUES( {cols} );'
        rslt = connectToMySQL(DATABASE).query_db(query, beer_info)
        return rslt

    @classmethod
    def rate_beer(cls, rating_info):
        query = f"INSERT INTO {cls.MTM_TABLE_NAME}( {', '.join(cls.MTM_COLUMN_NAMES)} ) "
        cols = ', '.join([f'%({tag})s' for tag in cls.MTM_COLUMN_NAMES])
        query += f'VALUES( {cols} ) '
        query += "ON DUPLICATE KEY UPDATE "
        for tag in cls.MTM_COLUMN_NAMES:
            if tag != 'users_id' or tag != 'beers_id':
                query += f"{tag} = {rating_info[tag]}{',' if tag != 'val' else ';'} "
        rslt = connectToMySQL(DATABASE).query_db(query, rating_info)
        return rslt
    
    @classmethod
    def get_all_rated_beers(cls, user_id):
        query = f'SELECT {cls.TABLE_NAME}.* FROM {cls.MTM_TABLE_NAME} '
        query += f'LEFT JOIN {cls.TABLE_NAME} ON {cls.MTM_TABLE_NAME}.beers_id = {cls.TABLE_NAME}.id '
        query += f'WHERE users_id = {user_id};'
        rslt = connectToMySQL(DATABASE).query_db(query)
        if not rslt:
            return False
        breweries = [cls(brewery) for brewery in rslt]
        return breweries

    @classmethod
    def update_beer(cls, new_info):
        valid_info = cls.validate_new_beer(new_info)
        if not valid_info:
            return False
        query = f'UPDATE {cls.TABLE_NAME} '
        cols = ', '.join([f'{tag} = %({tag})s' for tag in cls.COLUMN_NAMES])
        query += f'SET {cols} '
        query += 'WHERE id = %(id)s;'
        rslt = connectToMySQL(DATABASE).query_db(query, new_info)
        return rslt

    @classmethod
    def delete_beer(cls, id):
        query = f'DELETE FROM {cls.TABLE_NAME} '
        query += f'WHERE id = {id};'
        rslt = connectToMySQL(DATABASE).query_db(query)
        return rslt