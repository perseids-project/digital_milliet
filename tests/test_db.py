import os
import json
import yaml
from unittest import TestCase
from digital_milliet.digital_milliet import DigitalMilliet
from tests.test_dm import DigitalMillietTestCase
from flask import Flask


class TestDb(DigitalMillietTestCase):

    def test_db_setup(self):
        with self.app.app_context():
            rec = self.mongo.db.annotation.find_one()
            self.assertIsNotNone(rec, "Couldn't find the seeded record")
            self.assertIsNotNone(rec['_id'], "Record doesn't have an id")
            self.assertIsNotNone(
                rec['bibliography'],
                "Record doesn't have a bibliography")
            self.assertIsNotNone(
                rec['commentary'],
                "Record doesn't have a commentary")
            self.assertIsNotNone(
                rec['translation'],
                "Record doesn't have a translation")
            self.assertEqual(
                rec['bibliography'][0]['hasBody']['@id'],
                'http://perseids.org/collections/urn:cite:perseus:digmil.261.b1',
                "Unexpected data")
