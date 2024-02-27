import os 
from sqlalchemy import create_engine

class Config(object):
    SECRET_KEY='SECRET'
    SESSION_COOKIE_SECURE=False

class DevelopmentConfig(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:@localhost:3306/bd_idgs802'

