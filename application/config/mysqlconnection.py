import logging
import pymysql.cursors
import os
from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

class MySQLConnection:
    def __init__(self, db):
        connection = pymysql.connect(host = os.environ.get("HOST"),
                                    user = os.environ.get("DB_USER"), 
                                    password = os.environ.get("DB_PASSWORD"), 
                                    db = db,
                                    charset = 'utf8mb4',
                                    cursorclass = pymysql.cursors.DictCursor,
                                    autocommit = True)
        self.connection = connection
    def query_db(self, query, data=None):
        with self.connection.cursor() as cursor:
            try:
                query = cursor.mogrify(query, data)
                logging.debug(f'Running Query: {query}')
                cursor.execute(query, data)
                if query.lower().find("insert") >= 0:
                    self.connection.commit()
                    return cursor.lastrowid
                elif query.lower().find("select") >= 0:
                    result = cursor.fetchall()
                    return result
                else:
                    self.connection.commit()
            except Exception as e:
                logging.error(f'Something went wrong {e}')
                return False
            finally:
                self.connection.close() 
def connectToMySQL(db):
    return MySQLConnection(db)