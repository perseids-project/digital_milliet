import os
import yaml
from digital_milliet.digital_milliet import DigitalMilliet
from flask import Flask
from tests.test_dm import DigitalMillietTestCase


class TestIdentifierList(DigitalMillietTestCase):
    def setUp(self):
        self.app = Flask('digital_milliet')
        self.dm = self.make_dm(app=self.app,
                               config_files=["../tests/testconfig.cfg"])
        self.client = self.app.test_client()
        self.fixture = os.path.join(os.path.dirname(__file__), 'dbfixture.yml')
        self.mongo = self.dm.get_db()
        self.setupDb()
        self.setupSession()

    def test_get_milliet_identifier_list(self):
        with self.app.app_context():
            expected_identifier_list = ["261", "999"]
            identifier_list = self.dm.commentaries.get_milliet_identifier_list()
            self.assertEqual(expected_identifier_list, identifier_list)

    def test_get_surrounding_identifier(self):
        with self.app.app_context():
            expected_identifier_pair = (None, "999")
            identifier_pair = self.dm.commentaries.get_surrounding_identifier(
                "261")
            self.assertEqual(expected_identifier_pair, identifier_pair)

            expected_identifier_pair = ("261", None)
            identifier_pair = self.dm.commentaries.get_surrounding_identifier(
                "999")
            self.assertEqual(expected_identifier_pair, identifier_pair)
