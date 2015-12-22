from flask import Flask
from flask.ext.cors import CORS
from flask.ext.pymongo import PyMongo
from flask_bower import Bower
from flaskext.markdown import Markdown

app = Flask(__name__, template_folder="templates")
cors = CORS(app)
mongo = PyMongo(app)
bower = Bower(app)
markdown = Markdown(app)

from app import views
