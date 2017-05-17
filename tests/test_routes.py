import json
import re
from unittest import TestCase
from tests.test_dm import DigitalMillietTestCase


class TestRoutes(DigitalMillietTestCase, TestCase):

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
        rv = self.client.get('/search?in=Author&query=Xenophon').data.decode()
        self.assertIn('Memorabilia',rv,"Search result missing")

    def test_commentary(self):
        rv = self.client.get('/commentary').data.decode()
        self.assertIn('<li>261 <a href="commentary/261">View</a> <a href="edit/261">Edit</a></li>',rv,"Missing Commentary List Item")

    def test_commentary_by_millnum(self):
        rv = self.client.get('/commentary/261').data.decode()
        self.assertIn('<h2>Xenophon, Memorabilia 3.10.1-3.10.5</h2>',rv,'Header Info Missing')
        self.assertNotIn("id=\"mirador-container", rv, "Mirador container should not show for text without images")

    def test_api(self):
        rv = json.loads(self.client.get('/api/commentary/261').data.decode())
        self.assertIn("bibliography", rv, 'API Response Invalid')

    def test_new_no_session(self):
        rv = self.client.get('/new')
        self.assertEqual('http://localhost/oauth/login?next=http%3A%2F%2Flocalhost%2Fnew',rv.location, "Doesn't redirect to login")

    def test_new_with_session(self):
        with self.client.session_transaction() as sess:
            sess['oauth_user_uri'] = 'http://sosol.perseids.org/sosol/User/MyTestUser'
        rv = self.client.get('/new').data.decode()
        self.assertIn('Enter Commentary',rv,"Not the new record page")

    def test_edit_no_session(self):
        rv = self.client.get('/edit/261')
        self.assertEqual('http://localhost/oauth/login?next=http%3A%2F%2Flocalhost%2Fedit%2F261',rv.location, "Doesn't redirect to login")

    def test_edit_with_session(self):
        with self.client.session_transaction() as sess:
            sess['oauth_user_uri'] = 'http://sosol.perseids.org/sosol/User/MyTestUser'
        rv = self.client.get('/edit/261').data.decode()
        self.assertIn('<h2>Edit Commentary :  261</h2>', rv, "Not the commentary page")

    def test_create_no_session(self):
        rv = self.client.post('/create', data = dict(l1text='New text'))
        self.assertEqual('http://localhost/oauth/login?next=http%3A%2F%2Flocalhost%2F',rv.location, "Doesn't redirect to index")

    def test_create_with_session(self):
        with self.client.session_transaction() as sess:
            sess['oauth_user_uri'] = 'http://sosol.perseids.org/sosol/User/MyTestUser'
            sess['oauth_user_name'] = 'Test User'
        submit_data = dict(
            milnum="123",
            l1uri="urn:cts:greekLit:tlg0012.tlg001.perseus-grc2:1-1",
            l1text="Οἱ πλεῖστοι τῶν περὶ",
            select_l1="grc",
            c1text="commentary",
            b1text="bibliography",
            t1uri="urn:cts:greekLit:tlg0032.tlg002.perseus-eng1:1-1",
            t1text="Dummy translation",
            own_uri_t1="",
            lang_t1="eng",
            t2text="french translation",
            t2lang="fra",
            own_uri_t2="",
            t2uri="",
            lang_t2="eng"
        )
        submit_data["iiif[]"] = [
            "http://free.iiifhosting.com/iiif/2ce9baa6bfa77047c690cfd31028685c8d29802766a44cddd39975440cab9b8/info.json",
            "http://iiif.biblissima.fr/manifests/ark:/12148/btv1b90068354/manifest.json"
        ]
        submit_data["iiif_publisher[]"] = [
            "Unknown",
            "Biblissima"
        ]
        rv = self.client.post('/create', data=submit_data)
        self.assertEqual(rv.status_code, 302)
        self.assertIn("/commentary/123", rv.location)

        with self.app.app_context():
            rec, auth = self.dm.parser.get_milliet("123")
        self.assertEqual(rec['creator']['@id'], "http://sosol.perseids.org/sosol/User/MyTestUser")
        self.assertEqual(rec['creator']['name'], "Test User")
        self.assertCountEqual(
            rec["images"],
            [
                {'location': 'Unknown',
                 'manifestUri': 'http://free.iiifhosting.com/iiif/2ce9baa6bfa77047c690cfd31028685c8d29802766a44cddd3997'
                                '5440cab9b8/info.json'},
                {'location': 'Biblissima',
                 'manifestUri': 'http://iiif.biblissima.fr/manifests/ark:/12148/btv1b90068354/manifest.json'}
            ]
        )

        rv = self.client.get('/commentary/123').data.decode()
        self.assertIn("id=\"mirador-container", rv, "Mirador container should not show for text without images")

    def test_save_edit_no_session(self):
        rv = self.client.post('/edit/save_edit', data = dict(c1text='Replacing the text'))
        self.assertEqual('http://localhost/oauth/login?next=http%3A%2F%2Flocalhost%2F',rv.location, "Doesn't redirect to index")

    def test_save_edit_with_session_add_image(self):
        with self.client.session_transaction() as sess:
            sess['oauth_user_uri'] = 'http://sosol.perseids.org/sosol/User/MyTestUser'
        rv1 = self.client.get('/edit/261').data.decode()
        m = re.search("name='mongo_id' value=(.*)>",rv1).group(1)

        # First Edit Check : adding images
        self.update_and_assert(self.make_update_data(
                mongo_id=m,
                iiif=[
                    "http://free.iiifhosting.com/iiif/2ce9baa6bfa77047c690cfd31028685c8d29802766a44cddd39975440cab9b8/info.json",
                    "http://iiif.biblissima.fr/manifests/ark:/12148/btv1b90068354/manifest.json"
                ],
                iiif_publisher=["Unknown", "Biblissima"]
        ))
        rec = self.get_rec()
        self.assertCountEqual(
            rec["images"],
            [
                {'location': 'Unknown',
                 'manifestUri': 'http://free.iiifhosting.com/iiif/2ce9baa6bfa77047c690cfd31028685c8d29802766a44cddd3997'
                                '5440cab9b8/info.json'},
                {'location': 'Biblissima',
                 'manifestUri': 'http://iiif.biblissima.fr/manifests/ark:/12148/btv1b90068354/manifest.json'}
            ]
        )

    def test_save_edit_with_session_edit_image(self):
        with self.client.session_transaction() as sess:
            sess['oauth_user_uri'] = 'http://sosol.perseids.org/sosol/User/MyTestUser'
        rv1 = self.client.get('/edit/261').data.decode()
        m = re.search("name='mongo_id' value=(.*)>",rv1).group(1)
        self.update_and_assert(self.make_update_data(
            mongo_id=m,
            iiif=[
                "http://free.iiifhosting.com/iiif/2ce9baa6bfa77047c690cfd31028685c8d29802766a44cddd39975440cab9b8/info.json",
                "http://iiif.biblissima.fr/manifests/ark:/12148/btv1b90068354/manifest.json"
            ],
            iiif_publisher=[
                "BNF",
                "Biblissima"
            ]
        ))
        rec = self.get_rec()
        self.assertCountEqual(
            rec["images"],
            [
                {'location': 'BNF',
                 'manifestUri': 'http://free.iiifhosting.com/iiif/2ce9baa6bfa77047c690cfd31028685c8d29802766a44cddd3997'
                                '5440cab9b8/info.json'},
                {'location': 'Biblissima',
                 'manifestUri': 'http://iiif.biblissima.fr/manifests/ark:/12148/btv1b90068354/manifest.json'}
            ]
        )

    def test_save_edit_with_session_delete_one_image(self):
        with self.client.session_transaction() as sess:
            sess['oauth_user_uri'] = 'http://sosol.perseids.org/sosol/User/MyTestUser'
        rv1 = self.client.get('/edit/261').data.decode()
        m = re.search("name='mongo_id' value=(.*)>", rv1).group(1)
        self.update_and_assert(self.make_update_data(
            mongo_id=m,
            iiif=[
                "http://iiif.biblissima.fr/manifests/ark:/12148/btv1b90068354/manifest.json"
            ],
            iiif_publisher=[
                "Biblissima"
            ]
        ))
        rec = self.get_rec()
        self.assertCountEqual(
            rec["images"],
            [
                {'location': 'Biblissima',
                 'manifestUri': 'http://iiif.biblissima.fr/manifests/ark:/12148/btv1b90068354/manifest.json'}
            ]
        )

    def test_save_edit_with_session_delete_all_image(self):
        with self.client.session_transaction() as sess:
            sess['oauth_user_uri'] = 'http://sosol.perseids.org/sosol/User/MyTestUser'
        rv1 = self.client.get('/edit/261').data.decode()
        m = re.search("name='mongo_id' value=(.*)>", rv1).group(1)
        self.update_and_assert(self.make_update_data(mongo_id=m))
        rec = self.get_rec()
        self.assertCountEqual(
            rec["images"], []
        )

    def test_save_edit_with_session_check_no_duplicate_works(self):
        """ Check that editing a work does not add a duplicated passage """
        with self.client.session_transaction() as sess:
            sess['oauth_user_uri'] = 'http://sosol.perseids.org/sosol/User/MyTestUser'
        rv1 = self.client.get('/edit/261').data.decode()
        m = re.search("name='mongo_id' value=(.*)>", rv1).group(1)
        self.update_and_assert(self.make_update_data(mongo_id=m, t2_text="Hello there", lang2="fra"))
        # TODO : This should be changed when author are moved to their own collection
        with self.app.app_context():
            author = self.dm.mongo.db.annotation.find_one_or_404({"cts_id": "tlg0032"})
            self.assertCountEqual(
                author["works"][0]["millnums"], [['999', '3.10.1-3.10.5'], ['261', '3.10.1-3.10.5']],
                "There should be no passage duplication"
            )

    def test_save_edit_fix_corrupted(self):
        with self.client.session_transaction() as sess:
            sess['oauth_user_uri'] = 'http://sosol.perseids.org/sosol/User/MyTestUser'
        rv1 = self.client.get('/edit/999').data.decode()
        m = re.search("name='mongo_id' value=(.*)>",rv1).group(1)
        t1_text = re.search("t1_text",rv1)
        self.assertIsNotNone(t1_text)
        submit_data = dict(
            mongo_id = m,
            orig_uri ="urn:cts:greekLit:tlg0032.tlg002.perseus-grc2:3.10.1-3.10.5",
            orig_text= "",
            orig_lang="grc",
            c1text ="",
            b1text = "",
            t1_text = "some new translation text",
            lang1 = "eng",
            t2_text = "nouveau!",
            lang2 = "fra"
        )
        rv = self.client.post('/edit/save_edit', data=submit_data, follow_redirects=True)
        self.assertIn('Edit successfully saved',rv.data.decode(),"Missing success message")
        with self.app.app_context():
            rec,auth = self.dm.parser.get_milliet("999")
        self.assertEqual(rec['t1_text'],"some new translation text")

    def make_update_data(
            self,
            mongo_id,  iiif=[], iiif_publisher=[],
            orig_uri="urn:cts:greekLit:tlg0032.tlg002.perseus-grc2:3.10.1-3.10.5",
            orig_text="",
            orig_lang="grc",
            c1text="",
            b1text="",
            t1_uri="urn:cts:greekLit:tlg0032.tlg002.perseus-eng1:3.10.1-3.10.5",
            t2_text="",
            lang2=None
    ):
        submit_data = dict(
            mongo_id=mongo_id,
            orig_uri=orig_uri,
            orig_text=orig_text,
            orig_lang=orig_lang,
            c1text=c1text,
            b1text=b1text,
            t1_uri=t1_uri,
            t2_text=t2_text
        )
        if lang2:
            submit_data["lang2"] = lang2
        submit_data["iiif[]"] = iiif
        submit_data["iiif_publisher[]"] = iiif_publisher
        return submit_data

    def update_and_assert(self, data):
        rv = self.client.post('/edit/save_edit', data=data)
        self.assertEqual(rv.status_code, 302)
        self.assertIn("/commentary", rv.location)

    def get_rec(self, milliet_id="261"):
        with self.app.app_context():
            rec, auth = self.dm.parser.get_milliet(milliet_id)
        return rec