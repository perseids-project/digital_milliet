import os
import json
import yaml
from unittest import TestCase
from digital_milliet.digital_milliet import DigitalMilliet
from flask import Flask

class DigitalMillietTestCase(TestCase):

    def make_dm(self, app, **kwargs):
        return DigitalMilliet(app, **kwargs)

    def setUp(self):
        self.app = Flask('digital_milliet')
        self.dm = self.make_dm(app=self.app,config_file="../tests/testconfig.cfg")
        self.client = self.app.test_client()
        self.fixture = os.path.join(os.path.dirname(__file__), 'dbfixture.yml')
        self.mongo = self.dm.get_db()
        self.setupDb()
        self.setupSession()

    def setupDb(self):
        with self.app.app_context():
            self.mongo.db.annotation.drop()
            with open(self.fixture, 'r') as (stream):
                data = yaml.load(stream)
                self.mongo.db.annotation.insert_many(data)

    def setupSession(self):
        with self.client.session_transaction() as sess:
            sess['oauth_user_uri'] = None

    def teardownSession(self):
        with self.client.session_transaction() as sess:
            sess['oauth_user_uri'] = None

    def teardownDb(self):
        with self.app.app_context():
            self.mongo.db.annotation.drop()

    def tearDown(self):
        self.teardownDb()
        self.teardownSession()


