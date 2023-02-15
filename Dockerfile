FROM lambci/lambda:build-python3.9

RUN yum -y install flask flask-cors python-dotenv requests werkzeug pymysql