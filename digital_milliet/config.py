from .digital_milliet import app

class BaseConfig(object):
    MONGO_DBNAME = 'dev'

class DevelopmentConfig(BaseConfig):
    MONGO_DBNAME = 'dev'

class TestingConfig(BaseConfig):
    MONGO_DBNAME = 'test'


