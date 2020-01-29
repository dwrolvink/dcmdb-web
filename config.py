# Copy this file and rename the copy to config_local.py
# Then, fill in all the values in the new file

class Config(object):
    WEBSITE_NAME = '<fill in>'
    DEBUG = False
    TESTING = False
    SECRET_KEY = '<fill in secret key>'
    

class ProductionConfig(Config):
    DEBUG = True
    TESTING = False

class DevelopmentConfig(Config):
    DEVELOPMENT = False
    DEBUG = True
    TESTING = True

class TestingConfig(Config):
    TESTING = True
    TEMPLATES_AUTO_RELOAD = True
