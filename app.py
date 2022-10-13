import logging
logging.basicConfig(level=logging.DEBUG, filename="log.log", filemode="w",
    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
from application import app
from application.controllers import users_controller, breweries_controller, beers_controller

host = '127.0.0.1'
port = 5000

if __name__ == '__main__':
    logging.debug(f'App started at {host} on port {port}')
    app.run(host=host, port=port, debug=True)
    logging.debug(f'App stopped')
 