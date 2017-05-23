import os
import json
import re
import yaml
import datetime
from unittest import TestCase
from unittest.mock import patch
from digital_milliet.digital_milliet import DigitalMilliet
from tests.test_dm import DigitalMillietTestCase
from flask import Flask
import werkzeug


class TestDb(DigitalMillietTestCase):

    def test_save_from_form_fails_existing(self):
        submit_data = dict(
            milnum = '261',
            l1uri ="urn:cts:greekLit:tlg0032.tlg002.perseus-grc2:3.10.1-3.10.5",
            own_uri_l1 = "",
            select_l1 = "grc",
            l1text = "this is my text",
            c1text ="",
            b1text = "",
            t1uri = "urn:cts:greekLit:tlg0032.tlg002.perseus-eng1:3.10.1-3.10.5",
            t1text = "",
            own_uri_t1 = "",
            lang_t1 = "eng",
            t2uri = "",
            t2text = "some translation text",
            own_uri_t2 = "",
            lang_t2 = "fra"
        )
        with self.app.test_request_context():
          added = self.dm.commentaries.create_commentary(submit_data)
        self.assertIsNone(added,"Should not have added a new record")

    def test_save_from_form_succeeds_new(self):
        submit_data = dict(
            milnum = '111',
            l1uri ="urn:cts:greekLit:tlg0032.tlg002.perseus-grc2:3.10.1-3.10.5",
            own_uri_l1 = "",
            l1text = "this is my text",
            select_l1 = "grc",
            c1text ="",
            b1text = "",
            t1uri = "urn:cts:greekLit:tlg0032.tlg002.perseus-eng1:3.10.1-3.10.5",
            t1text = "",
            own_uri_t1 = "",
            lang_t1 = "eng",
            t2uri = "",
            t2text = "some translation text",
            own_uri_t2 = "",
            lang_t2 = "fra",
        )
        with self.app.test_request_context():
          added = self.dm.commentaries.create_commentary(submit_data)
        self.assertIsNotNone(added, "Should not have added a new record")
        self.assertEqual("111", added, "Unexpected response from save")

    def test_edit_save_does_not_overrwrite_uri(self):
        with self.client.session_transaction() as sess:
            sess['oauth_user_uri'] = 'http://sosol.perseids.org/sosol/User/MyTestUser'
        rv1 = self.client.get('/edit/261').data.decode()
        m = re.search("name='mongo_id' value=(.*)>",rv1).group(1)
        submit_data = dict(
            mongo_id = m,
            milnum = '999',
            orig_uri ="urn:cts:greekLit:tlg0032.tlg002.perseus-grc2:3.10.1-3.10.5",
            orig_text= "",
            orig_lang="grc",
            c1text ="",
            b1text = "",
            t1_uri = "urn:cts:greekLit:tlg0032.tlg002.perseus-eng1:3.10.1-3.10.5",
            t1_text = "",
            lang1 = "eng",
            t2_uri = "",
            t2_text = "some translation text",
            own_uri_t2 = "",
            lang2 = "fra",
        )
        with self.app.app_context():
            added = self.dm.commentaries.update_commentary(submit_data)
        self.assertIsNotNone(added, "Should not have added a new record")

    def test_validate_annotation(self):
        file = os.path.join(os.path.dirname(__file__), 'annotationtestfixtures.yml')
        with open(file, 'r') as (stream):
            data = yaml.load(stream)
        self.assertTrue(self.dm.commentaries.validate_annotation(data['valid']),"Should be a valid annotation")
        with self.assertRaises(ValueError) as context:
            self.dm.commentaries.validate_annotation(data['invalid_target'])
            self.assertTrue('Invalid commentary target') in context.exception
        with self.assertRaises(ValueError) as context:
            self.dm.commentaries.validate_annotation(data['invalid_translation1_body_uri'])
            self.assertTrue('Invalid translation 1 uri') in context.exception
        with self.assertRaises(ValueError) as context:
            self.dm.commentaries.validate_annotation(data['invalid_translation2_body_uri'])
            self.assertTrue('Invalid translation 2 uri') in context.exception


    def test_remove_it(self):
        with self.app.app_context():
          self.assertEqual(1,self.dm.authors.search(query='261', milliet_id=True).count())
          self.assertIsNotNone(self.dm.commentaries.get_milliet('261'))
          self.assertEqual(2,self.dm.commentaries.remove_milliet('261'))
          self.assertEqual(0,self.dm.authors.search(query='261', milliet_id=True).count())
          with self.assertRaises(werkzeug.exceptions.NotFound):
            self.assertIsNone(self.dm.commentaries.get_milliet('261'))

    def test_create_tag_annotation(self):
        tag = "dummytag"
        date = datetime.datetime.today()
        target ="http://dummytarget"
        expected = {
            "@context": "http://www.w3.org/ns/oa-context-20130208.json",
            "@type": "oa:Annotation",
            "annotatedAt": str(date),
            "hasTarget": target,
            "motivatedBy": "oa:tagging",
            "hasBody": {
                "@type": "oa:Tag",
                "chars": tag,
                "format": "text",
            }
        }
        with self.client.session_transaction() as sess:
            sess['oauth_user_uri'] = 'http://sosol.perseids.org/sosol/User/MyTestUser'
            sess['oauth_user_name'] = 'MyTestUser'
        with self.app.app_context():
            person = self.dm.commentaries.format_person_from_authentificated_user()
            expected["creator"] = person
            anno = self.dm.commentaries.create_tag_annotation(tag,target,person,date)
            self.assertIsNotNone(anno["@id"])
            self.assertIsNotNone(anno["hasBody"]["@id"])
            anno.pop("@id")
            anno["hasBody"].pop("@id")
            self.assertEqual(expected,anno)

    def test_create_semantic_tag_annotation(self):
        date = datetime.datetime.today()
        target ="http://dummytarget"
        with self.client.session_transaction() as sess:
            sess['oauth_user_uri'] = 'http://sosol.perseids.org/sosol/User/MyTestUser'
            sess['oauth_user_name'] = 'MyTestUser'
        for tag in [ "https://w3id.org/myorg/thisisasamplesemantictag",
                     "http://w3id.org/myorg/thisisasamplesemantictag"]:
            expected = {
                "@context": "http://www.w3.org/ns/oa-context-20130208.json",
                "@type": "oa:Annotation",
                "annotatedAt": str(date),
                "hasTarget": target,
                "motivatedBy": "oa:tagging",
                "hasBody": {
                    "@id": tag,
                    "@type": "oa:SemanticTag"
                }
            }
            with self.app.app_context():
                person = self.dm.commentaries.format_person_from_authentificated_user()
                expected["creator"] = person
                anno = self.dm.commentaries.create_tag_annotation(tag,target,person,date)
                self.assertIsNotNone(anno["@id"])
                anno.pop("@id")
                self.assertEqual(expected,anno)



