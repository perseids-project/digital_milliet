import os
import json
import re
import yaml
from unittest import TestCase
from digital_milliet.digital_milliet import DigitalMilliet
from tests.test_dm import DigitalMillietTestCase
from flask import Flask

class TestRoutes(DigitalMillietTestCase):

    def test_index(self):
        rv = self.client.get('/').data.decode()
        self.assertIn('Welcome to the home of the Digital Milliet!',rv,"Doesn't appear to be the index.html")

    def test_index_with_index(self):
        rv = self.client.get('/index').data.decode()
        self.assertIn('Welcome to the home of the Digital Milliet!',rv,"Doesn't appear to be the index.html")

    def test_about(self):
        rv = self.client.get('/about').data.decode()
        self.assertIn('What is the Digital Milliet?',rv,"Doesn't appear to be the aobut.html")

    def test_search(self):
        rv = self.client.post('/search', data = dict(dropdown='Author',value="Xenophon")).data.decode()
        self.assertIn('Memorabilia',rv,"Search result missing")

    def test_commentary(self):
        rv = self.client.get('/commentary').data.decode()
        self.assertIn('<li>261 <a href="commentary/261">View</a> <a href="edit/261">Edit</a></li>',rv,"Missing Commentary List Item")

    def test_commentary_by_millnum(self):
        rv = self.client.get('/commentary/261').data.decode()
        self.assertIn('<h2>Xenophon, Memorabilia 3.10.1-3.10.5 </h2>',rv,'Header Info Missing')

    def test_api(self):
        rv = self.client.get('/api/commentary/261').data.decode()
        self.assertIn('{\n  "bibliography',rv,'API Response Invalid')

    def test_edit_no_session(self):
        rv = self.client.get('/edit/261')
        self.assertEqual('http://localhost/oauth/login?next=http%3A%2F%2Flocalhost%2Fedit%2F261',rv.location, "Doesn't redirect to login")

    def test_edit_with_session(self):
        with self.client.session_transaction() as sess:
            sess['oauth_user_uri'] = 'http://sosol.perseids.org/sosol/User/MyTestUser'
        rv = self.client.get('/edit/261').data.decode()
        self.assertIn('<legend>Edit Commentary:</legend>',rv,"Not the commentary page")
        self.assertIn('<label for="milnum">Milliet Number:261</label>',rv,"Wrong record being edited")

    def test_save_edit_no_session(self):
        rv = self.client.post('/edit/save_edit', data = dict(c1text='Replacing the text'))
        self.assertEqual('http://localhost/oauth/login?next=http%3A%2F%2Flocalhost%2F',rv.location, "Doesn't redirect to index")

    def test_save_edit_with_session(self):
        with self.client.session_transaction() as sess:
            sess['oauth_user_uri'] = 'http://sosol.perseids.org/sosol/User/MyTestUser'
        rv1 = self.client.get('/edit/261').data.decode()
        m = re.search("name='mongo_id' value=(.*)>",rv1).group(1)
        submit_data = dict(
            mongo_id = m,
            orig_uri ="urn:cts:greekLit:tlg0032.tlg002.perseus-grc2:3.10.1-3.10.5",
            c1text ="",
            b1text = "",
            t1_uri = "urn:cts:greekLit:tlg0032.tlg002.perseus-eng1:3.10.1-3.10.5",
            t2_text = ""
        )
        rv = self.client.post('/edit/save_edit', data=submit_data, follow_redirects=True)
        self.assertIn('Edit successfully saved',rv.data.decode(),"Missing success message")





