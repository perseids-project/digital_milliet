import os
import yaml
from digital_milliet.digital_milliet import DigitalMilliet
from flask import Flask
from tests.test_dm import DigitalMillietTestCase


class TestTagSearch(DigitalMillietTestCase):
    def setUp(self):
        self.app = Flask('digital_milliet')
        self.dm = self.make_dm(app=self.app,config_file="../tests/testconfig.cfg")
        self.client = self.app.test_client()
        self.fixture = os.path.join(os.path.dirname(__file__), 'dbfixturetags.yml')
        self.mongo = self.dm.get_db()
        self.setupDb()
        self.setupSession()

    def test_search_tags(self):
        with self.app.app_context():
            expected_tags = { "dolphin": 1}
            expected_semantic_tags = { "http://w3id.org/myorg/mysemantictag": 1 }
            tags,semantic = self.dm.commentaries.get_existing_tags()
            self.assertEqual(expected_tags, tags)
            self.assertEqual(expected_semantic_tags, semantic)

