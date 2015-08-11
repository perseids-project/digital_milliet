from flask import Flask
from flask.ext.cors import CORS
from flask.ext.pymongo import PyMongo

app = Flask(__name__, template_folder="templates")
cors = CORS(app)
mongo = PyMongo(app)

from app import views
