# coding=utf8
from flask_babel import Babel
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_bower import Bower
from flaskext.markdown import Markdown

from digital_milliet.lib.author_builder import AuthorBuilder
from digital_milliet.lib.oauth import OAuthHelper
from digital_milliet.lib.commentaries import CommentaryHandler
from digital_milliet.lib.views import Views
from digital_milliet.lib.catalog import Catalog
from digital_milliet.lib.mirador import Mirador

import re
PERSONNA = re.compile("^\w\.\w+$")

class DigitalMilliet(object):
    """ The Digital Milliet Web Application """

    def __init__(self,app=None, config_file="config.cfg"):
        self.app = None

        if app is not None:
            self.app = app
            self.init_app(config_file)

    def init_app(self, config_file=None):

        self.app.config.from_pyfile(config_file, silent=False)
        self.app.secret_key = self.app.config['SECRET_KEY']
        self.bower = Bower(self.app)
        self.markdown = Markdown(self.app)
        self.cors = CORS(self.app)
        self.mongo = PyMongo(self.app)
        self.oauth = OAuthHelper(self.app)
        self.authors = AuthorBuilder(self.mongo, Catalog(self.app), app=self.app)
        self.commentaries = CommentaryHandler(db=self.mongo, authors=self.authors, config=self.app.config, auth=self.oauth)
        self.mirador = Mirador(db=self.mongo, app=self.app, parser=self.commentaries)
        self.babel = Babel(self.app)
        self.views = Views(self.app, self.commentaries, self.mongo, self.authors, self.mirador)

        @self.app.template_filter("clean_ref")
        def clean_ref(ref):
            """ Clean up repetition of references
            """

            spl = ref.split("-")
            if len(spl) == 2:
                if spl[0] == spl[1]:
                    ref = spl[0]
            spl = ref.split(".")
            if len(spl) == 2 and ref[0] == ref[2] and PERSONNA.match(ref) is not None:
                ref = spl[1].title()
            return ref

    def get_db(self):
        return self.mongo



