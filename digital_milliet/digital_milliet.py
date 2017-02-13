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
from .oauth import OAuthHelper

app = Flask(__name__)
config = {
    "development" : "digital_milliet.config.DevelopmentConfig",
    "testing" : "digital_milliet.config.TestingConfig",
    "default" : "digital_milliet.config.BaseConfig"
}

app.config.from_object(config["default"])
app.config.from_pyfile('config.cfg',silent=True)

bower = Bower(app)
mongo = PyMongo(app)
markdown = Markdown(app)
cors = CORS(app)
OAuthHelper(app)



