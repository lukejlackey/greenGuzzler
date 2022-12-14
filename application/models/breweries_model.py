from application import DATABASE
from application.models.users_model import User
from application.config.mysqlconnection import connectToMySQL
from application.models.model_functions import validate_data

class Brewery:
    
    TABLE_NAME = 'breweries'
    OTM_TABLE_NAME = 'beers'
    MTM_TABLE_NAME = 'users_go_to_breweries'
    COLUMN_NAMES = ['name', 'type', 'address', 'state', 'city', 'zip', 'poster_id']
    MTM_COLUMN_NAMES = ['users_id','breweries_id']
    BASIC_CONSTRUCTOR_ATTRS = COLUMN_NAMES + ['id', 'poster_first_name', 'poster_last_name', 'poster_avatar', 'visitors']
    NAME_LENGTH = 1
    ZIP_MIN = 501
    ZIP_MAX = 99950
    STATES = {"AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California","CO":"Colorado","CT":"Connecticut","DE":"Delaware","FL":"Florida","GA":"Georgia","HI":"Hawaii","ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland","MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana","NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina","ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island","SC":"South Carolina","SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia","WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming"}
    BREWERY_TYPES = ['Nano', 'Micro', 'Pub', 'Regional', 'Regional Craft', 'Large']
    
    
    def __init__(self, data) -> None:
        for (k, v) in data.items():
            if k in self.BASIC_CONSTRUCTOR_ATTRS and k != 'type':
                setattr(self, k, v)
            elif k == 'type':
                setattr(self, k, self.BREWERY_TYPES[v])

    @classmethod
    def get_all_breweries(cls):
        query = f"SELECT * FROM {cls.TABLE_NAME} "
        query += f'LEFT JOIN {User.TABLE_NAME} ON {cls.TABLE_NAME}.poster_id = {User.TABLE_NAME}.id '        
        query += f'ORDER BY {cls.TABLE_NAME}.id DESC;'
        rslt = connectToMySQL(DATABASE).query_db(query)
        if not rslt:
            return False
        breweries = [cls(brewery) for brewery in rslt]
        return breweries

    @classmethod
    def get_all_user_breweries(cls, user_id):
        query = f'SELECT {cls.TABLE_NAME}.* FROM {cls.TABLE_NAME} '
        query += f'WHERE poster_id = {user_id};'
        rslt = connectToMySQL(DATABASE).query_db(query)
        if not rslt:
            return False
        breweries = [cls(brewery) for brewery in rslt]
        return breweries

    @classmethod
    def get_brewery(cls, id):
        query = f"SELECT {cls.TABLE_NAME}.*, poster.first_name AS poster_first_name, poster.last_name AS poster_last_name, poster.avatar AS poster_avatar, poster.id AS poster_id, COUNT({cls.MTM_TABLE_NAME}.users_id) AS visitors FROM {cls.TABLE_NAME} "
        query += f"LEFT JOIN {User.TABLE_NAME} AS poster ON {cls.TABLE_NAME}.poster_id = poster.id "
        query += f'LEFT JOIN {cls.MTM_TABLE_NAME} ON {cls.TABLE_NAME}.id = {cls.MTM_TABLE_NAME}.breweries_id '
        query += f'LEFT JOIN {User.TABLE_NAME} ON {cls.MTM_TABLE_NAME}.users_id = {User.TABLE_NAME}.id '
        query += f'WHERE {cls.TABLE_NAME}.id = {id};'
        rslt = connectToMySQL(DATABASE).query_db(query)
        if not rslt:
            return False
        brewery = cls(rslt[0])
        return brewery

    @classmethod
    def validate_create_brewery(cls, brewery_info):
        validations = {
            'name' : {
                'tag' : 'error_create_brewery_name',
                'msg' : f'Your brewery name must be at least {cls.NAME_LENGTH} characters long.',
                'condition' : len(brewery_info['name']) >= cls.NAME_LENGTH
            },
            'address' : {
                'tag' : 'error_create_brewery_address',
                'msg' : 'Address is required.',
                'condition' : None
            },
            'city' : {
                'tag' : 'error_create_brewery_city',
                'msg' : 'City is required.',
                'condition' : None
            },
            'zip' : {
                'tag' : 'error_create_brewery_zip',
                'msg' : 'Please enter a valid zip.',
                'condition' : cls.ZIP_MIN <= int(brewery_info['zip'] if brewery_info['zip'] else cls.ZIP_MIN - 1) <= cls.ZIP_MAX
            }
        }
        validity = validate_data(brewery_info, validations)
        return validity

    @classmethod
    def create_new_brewery(cls, brewery_info):
        valid_info = cls.validate_create_brewery(brewery_info)
        if not valid_info:
            return False
        query = f"INSERT INTO {cls.TABLE_NAME}( {', '.join(cls.COLUMN_NAMES)} ) "
        cols = ', '.join([f'%({tag})s' for tag in cls.COLUMN_NAMES])
        query += f'VALUES( {cols} );'
        rslt = connectToMySQL(DATABASE).query_db(query, brewery_info)
        return rslt
    
    @classmethod
    def visit_brewery(cls, visit_info):
        query = f"INSERT INTO {cls.MTM_TABLE_NAME}( {', '.join(cls.MTM_COLUMN_NAMES)} ) "
        cols = ', '.join([f'%({tag})s' for tag in cls.MTM_COLUMN_NAMES])
        query += f'VALUES( {cols} );'
        rslt = connectToMySQL(DATABASE).query_db(query, visit_info)
        return rslt
    
    @classmethod
    def get_all_visited_breweries(cls, user_id):
        query = f'SELECT {cls.TABLE_NAME}.* FROM {cls.MTM_TABLE_NAME} '
        query += f'LEFT JOIN {cls.TABLE_NAME} ON {cls.MTM_TABLE_NAME}.breweries_id = {cls.TABLE_NAME}.id '
        query += f'WHERE users_id = {user_id};'
        rslt = connectToMySQL(DATABASE).query_db(query)
        if not rslt:
            return False
        breweries = [cls(brewery) for brewery in rslt]
        return breweries

    @classmethod
    def update_brewery(cls, new_info):
        valid_info = cls.validate_create_brewery(new_info)
        if not valid_info:
            return False
        query = f'UPDATE {cls.TABLE_NAME} '
        cols = ', '.join([f'{tag} = %({tag})s' for tag in cls.COLUMN_NAMES])
        query += f'SET {cols} '
        query += 'WHERE id = %(id)s;'
        rslt = connectToMySQL(DATABASE).query_db(query, new_info)
        return rslt

    @classmethod
    def delete_brewery(cls, id):
        query = f'DELETE FROM {cls.TABLE_NAME} '
        query += f'WHERE id = {id};'
        rslt = connectToMySQL(DATABASE).query_db(query)
        return rslt