# coding=utf8
from flask.ext.babel import Babel
from flask.ext.cors import CORS
from flask.ext.pymongo import PyMongo
from flask_bower import Bower
from flaskext.markdown import Markdown

from digital_milliet.lib.author_builder import AuthorBuilder
from digital_milliet.lib.oauth import OAuthHelper
from digital_milliet.lib.parser import Parser
from digital_milliet.lib.views import Views
from digital_milliet.lib.catalog import Catalog


class DigitalMilliet(object):
    """ The Digital Milliet Web Application """


    def __init__(self,app=None,config_file="config.cfg"):
        self.app = None


        if app is not None:
            self.app = app
            self.init_app(config_file)

    def init_app(self,config_file=None):

        config = {
            "development" : "digital_milliet.lib.config.DevelopmentConfig",
            "testing" : "digital_milliet.lib.config.TestingConfig",
            "default" : "digital_milliet.lib.config.BaseConfig"
        }
        self.app.config.from_object(config["default"])
        self.app.config.from_pyfile(config_file,silent=False)
        self.app.secret_key = self.app.config['SECRET_KEY']
        self.bower = Bower(self.app)
        self.markdown = Markdown(self.app)
        self.cors = CORS(self.app)
        self.mongo = PyMongo(self.app)
        self.oauth = OAuthHelper(self.app)
        self.builder = AuthorBuilder(self.mongo,Catalog(self.app))
        self.parser = Parser(db=self.mongo, builder=self.builder, config=self.app.config, auth=self.oauth)
        self.babel = Babel(self.app)
        self.views = Views(self.app, self.parser, self.mongo, self.builder)

    def get_db(self):
        return self.mongo



