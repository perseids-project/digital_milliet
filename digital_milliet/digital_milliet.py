# coding=utf8
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session, Response, make_response
from flask.ext.cors import CORS
from flask.ext.pymongo import PyMongo
from flask_bower import Bower
from flaskext.markdown import Markdown
from os.path import expanduser
from os.path import expanduser
import bson
from bson.objectid import ObjectId
from bson.json_util import dumps
import re
import json
from digital_milliet.oauth import OAuthHelper
from digital_milliet.data_parse import Parser
from digital_milliet.author_builder import AuthorBuilder
from digital_milliet.views import Views

class DigitalMilliet(object):
    """ The Digital Milliet Web Application """


    def __init__(self,app=None,config_file="config.cfg"):
        self.app = None


        if app is not None:
            self.app = app
            self.init_app(config_file)

    def init_app(self,config_file=None):

        config = {
            "development" : "digital_milliet.config.DevelopmentConfig",
            "testing" : "digital_milliet.config.TestingConfig",
            "default" : "digital_milliet.config.BaseConfig"
        }
        self.app.config.from_object(config["default"])
        self.app.config.from_pyfile(config_file,silent=False)
        self.bower = Bower(self.app)
        self.markdown = Markdown(self.app)
        self.cors = CORS(self.app)
        self.mongo = PyMongo(self.app)
        self.oauth = OAuthHelper(self.app)
        self.parser = Parser(self.mongo)
        self.builder = AuthorBuilder(self.app, self.mongo)
        self.views = Views(self.app, self.parser, self.mongo, self.builder)


