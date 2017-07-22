import os
class Config(object):
    pass

class ProdConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR,'ca.db')
    DATABASE_CONNECT_OPTIONS = {}
    CSRF_ENABLED = True
    CSRF_SESSION_KEY = "48644fbc-fbc0-478e-8815-33535a46428d"
    SECRET_KEY = "13bcf584-d591-45b7-8e28-6c61e635fc2b"
    SQLALCHEMY_TRACK_MODIFICATIONS = False