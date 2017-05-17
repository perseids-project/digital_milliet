import datetime
from uuid import uuid4
import re
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from MyCapytain.common.reference import URN


class CommentaryHandler(object):
    """ Parses data for retrieval/storage to/from the database
    """
    def __init__(self, db=None, builder=None, config=None, auth=None):
        """ CommentaryHandler object

        :param db: Mongo Db Handle
        :type db: PyMongo
        :param builder:  helper for building new Author records
        :type builder: AuthorBuilder
        :param config: configuration dictionary
        :type config: dict
        """

        self.mongo = db
        self.builder = builder
        self.config = config
        self.auth = auth

    def create_commentary(self, form):
        """Save a new set of annotations from the input form

        :param form: key/value pairs from input form
        :type form: dict

        :return: the Milliet number for the saved annotations or None if the record couldn't be saved
        :rtype: string
        """
        data = self.form_to_OpenAnnotation(form)
        cid = data["commentary"][0]["hasBody"]["@id"]
        exists = self.mongo.db.annotation.find_one({"commentary.hasBody.@id": cid})

        if not exists and self.validate_annotation(data):
            self.mongo.db.annotation.insert(data)
            # Now compile author info
            self.builder.author_db_build(data)
            return form["milnum"]
        else:
            return None

    def update_commentary(self, form):
        """Save an edited set of annotations to the db

        :param form: key/value pairs from edit form
        :type form: dict

        :return: True if successful False if not
        :rtype: bool
        """

        modtime = datetime.datetime.utcnow().isoformat()
        record = self.mongo.db.annotation.find_one_or_404({'_id': ObjectId(form['mongo_id'])})
        record['commentary'][0]['hasBody']['chars'] = form['c1text']
        record['bibliography'][0]['hasBody']['chars'] = form['b1text']
        cite_urn = record['commentary'][0]['hasBody']['@id']
        millnum = cite_urn.split('.')[2]

        if 't1_text' in form:
            if form['t1_text'] != '':
                if not isinstance(record['translation'][0]['hasBody'], dict):
                    # if we have switched from a uri to text then make sure we have the structure in place
                    record['translation'][0]['hasBody'] = self.format_translation_annotation("t1", millnum, form['t1_text'], None, None, form['lang1'])
                else:
                    record['translation'][0]['hasBody']['chars'] = form['t1_text']
                    record['translation'][0]['hasBody']['language'] = form['lang1']
        else:
            record['translation'][0]['hasBody'] = form['t1_uri']

        if 't2_text' in form:
            if form['t2_text'] != '':
                if not isinstance(record['translation'][1]['hasBody'], dict):
                    # if we have switched from a uri to text then make sure we have the structure in place
                    record['translation'][1]['hasBody'] = self.format_translation_annotation("t2", millnum, form['t2_text'], None, None, form['lang2'])
                else:
                    record['translation'][1]['hasBody']['chars'] = form['t2_text']
                    record['translation'][1]['hasBody']['language'] = form['lang2']
        else:
              record['translation'][1]['hasBody'] = form['t2_uri']

        record['commentary'][0]['modified'] = modtime
        record['bibliography'][0]['modified'] = modtime
        record['translation'][0]['modified'] = modtime
        record['translation'][1]['modified'] = modtime

        if form['orig_uri'] != '':
            record['translation'][0]['hasTarget'] = form['orig_uri']
            record['translation'][1]['hasTarget'] = form['orig_uri']

        self.update_contributors(record['commentary'][0])
        self.update_contributors(record['bibliography'][0])
        self.update_contributors(record['translation'][0])
        self.update_contributors(record['translation'][1])

        if not isinstance(record['commentary'][0]['hasTarget'], list):
            main_text = {
                "@id": self.format_uri(millnum, 'l1'),
                 "format": "text",
                 "chars": "",
                 "language": ""
            }
            record['commentary'][0]['hasTarget'] = ["", main_text]
        record['commentary'][0]['hasTarget'][0] = form['orig_uri']
        record['commentary'][0]['hasTarget'][1]['chars'] = form['orig_text']
        record['commentary'][0]['hasTarget'][1]['language'] = form['orig_lang']

        rv = None
        if self.validate_annotation(record):
            rv = self.mongo.db.annotation.save(record)
            self.builder.author_db_build(record)
        return rv

    def form_to_OpenAnnotation(self, form):
        """ Make a structure for the annotation from a set of key/value pairs

        :param form: key/value pairs from the form
        :type form: dict
        :return: the annotation
        :rtype: dict

        """
        date = datetime.datetime.today()
        milnum = form['milnum'].zfill(3)
        person = self.format_person_from_authentificated_user()
        primary_source_uri = ""
        if form['l1uri']:
            primary_source_uri = form['l1uri']
        elif form['own_uri_l1']:
            primary_source_uri = form['own_uri_l1']

        main_text = {
            "@id": self.format_uri(milnum, 'l1'),
            "format": "text",
            "chars": form['l1text'],
            "language": form['select_l1']
        }
        annotation = {
            "commentary": [
                {
                    "@context": "http://www.w3.org/ns/oa-context-20130208.json",
                    "@id": self.generate_uuid(),
                    "@type": "oa:Annotation",
                    "annotatedAt": str(date),
                    "creator": person,
                    "hasBody": {
                        "@id": self.format_uri(milnum, 'c1'),
                        "format": "text",
                        "chars": form['c1text'],
                        "language": "eng",
                    },
                    "hasTarget": [primary_source_uri, main_text],
                    "motivatedBy": "oa:commenting"
                }
            ],
            "bibliography": [
                {
                    "@context": "http://www.w3.org/ns/oa-context-20130208.json",
                    "@id": self.generate_uuid(),
                    "@type": "oa:Annotation",
                    "annotatedAt": str(date),
                    "creator": person,
                    "hasBody": {
                        "@id": self.format_uri(milnum, 'b1'),
                        "format": "text",
                        "chars": form['b1text'],
                        "language": "eng"
                    },
                    "hasTarget": self.format_uri(milnum, 'c1'),
                    "motivatedBy": "oa:linking"
                }
            ],
            "translation": [
                {
                    "@context": "http://www.w3.org/ns/oa-context-20130208.json",
                    "@id": self.generate_uuid(),
                    "@type": "oa:Annotation",
                    "annotatedAt": str(date),
                    "creator": person,
                    "hasBody": self.format_translation_annotation(
                        "t1", form['milnum'], form['t1text'],
                        form['t1uri'], form['own_uri_t1'], form['lang_t1']
                    ),
                    "hasTarget": primary_source_uri,
                    "motivatedBy": "oa:linking"
                },
                {
                    "@context": "http://www.w3.org/ns/oa-context-20130208.json",
                    "@id": self.generate_uuid(),
                    "@type": "oa:Annotation",
                    "annotatedAt": str(date),
                    "creator": person,
                    "hasBody": self.format_translation_annotation(
                        "t2", form['milnum'], form['t2text'],
                        form['t2uri'], form['own_uri_t2'], form['lang_t2']
                    ),
                    "hasTarget": primary_source_uri,
                    "motivatedBy": "oa:linking"
                }
            ],
            "tags": [],
            "images": []
        }
        if "iiif" in form:
            annotation["images"] = list([
                {
                    "@context": {
                        "oa": "http://www.w3.org/ns/oa-context-20130208.json",
                        "dc": "http://purl.org/dc/elements/1.1/"
                    },
                    "@id": self.generate_uuid(),
                    "@type": "oa:Annotation",
                    "oa:annotatedAt": str(date),
                    "oa:hasBody": {
                        "@id": manifest_uri,
                        "dc:publisher": publisher
                    },
                    "oa:hasTarget": self.format_uri(milnum, 'c1'),
                    "oa:motivatedBy": "oa:linking"
                }
                for manifest_uri, publisher in zip(form["iiif"], form["iiif_publisher"])
            ])
        return annotation

    def generate_uuid(self):
        """Create a unique id for an annotation

        :return: uid
        :rtype: string
        """
        uuid = 'digmilann.' + str(uuid4())
        return uuid

    def format_translation_annotation(self, num, milnum, text, uri, own_uri, lang):
        """ Build the body of a translation annotation.

        :param num: the translation identifier (t1 or t2)
        :type num: string
        :param milnum: the Milliet number for the annotation
        :type milnum: string
        :param text: the text of the translation (None if uri or own_uri is supplied)
        :type text: String
        :param uri: the uri of a translation - this is expected to be a CTS URN that appears in the linked cts repository
        :type uri: string
        :param own_uri: an user-supplied uri for a translation - this is for an externally linked translation text
        :type own_uri: string
        :param lang: the language code of the translation ('fra' or 'eng')
        :type lang: string

        :return: the body of the translation annotation
        :rtype: string (for a URI) or dict (if an embedded body)
        """
        if not uri and not own_uri:
            body = {
              "@id": self.format_uri(milnum, num),
              "format": "text",
              "chars": text,
              "language": lang
            }
        elif not uri and own_uri:
            body = own_uri
        else:
            body = uri

        return body

    def get_milliet(self, milliet_id):
        """Get the first set of annotations that target the supplied Milliet Number

        :param milliet_id:  Milliet Number
        :type milnum: string
        :return: Tuple where first element is the set of annotations and the second the author informations
        :rtype: (dict, dict)

        :raises 404 Not Found Exception: if the annotation is not found
        """
        obj = self.mongo.db.annotation.find_one_or_404({"commentary.hasBody.@id": self.format_uri(milliet_id, 'c1')})
        parsed_obj = self.simplify_milliet(obj)
        parsed_obj["millnum"] = milliet_id
        info = self.mongo.db.annotation.find_one({
            'works.millnums': {
                '$elemMatch': {
                    '$elemMatch': {
                        '$in': [milliet_id]
                    }
                }
            }
        })
        auth_info = {}
        if info is None:
            auth_info['auth'] = ""
            auth_info['work'] = ""
            auth_info['passage'] = ""
        else:
            auth_info['auth'] = info['name']
            for w in info['works']:
                for tup in w['millnums']:
                    if milliet_id in tup:
                        auth_info['work'] = w['title']
                        auth_info['passage'] = tup[1]
        return parsed_obj, auth_info

    def simplify_milliet(self, annotation_set):
        """ Parse a db record into a dict setup for views

        :param annotation_set: the db record
        :type annotation_set: dict
        :return:  Parsed version of the record
        :rtype: dict
        """
        result = dict()
        result['mid'] = annotation_set['_id']
        result['bibl'] = annotation_set['bibliography'][0]['hasBody']['chars']
        result['comm'] = annotation_set['commentary'][0]['hasBody']['chars']
        result["comm@id"] = annotation_set["commentary"][0]["hasBody"]["@id"]

        if 'creator' in annotation_set['commentary'][0]:
            result['creator'] = annotation_set['commentary'][0]['creator']
        else:
            result['creator'] = None

        if 'contributor' in annotation_set['commentary'][0]:
            result['contributor'] = annotation_set['commentary'][0]['contributor']
        else:
            result['contributor'] = None

        tnum = 0
        for transl in annotation_set['translation']:
            tnum += 1
            if isinstance(transl['hasBody'], dict):
                t_num = transl['hasBody']['@id'].split('.')[-1]
                text = transl['hasBody']['chars']
                lang = transl['hasBody']['language']
                result[t_num+'_text'] = text
                result[t_num+'_lang'] = lang
            else:
                t_num = "t" + str(tnum)
                text = transl['hasBody']
                try:
                    lang = re.search('\D+', text.split('-')[1]).group(0)
                    result[t_num+'_uri'] = text
                    result[t_num+'_lang'] = lang
                except:
                    # invalid URN we need to recover
                    result[t_num+'_text'] = text
                    result[t_num+'_lang'] = "eng"
                    pass

        # List is executed to avoid generators
        result["images"] = [
            {
                "manifestUri": iiif_anno['oa:hasBody']["@id"],
                "location": iiif_anno['oa:hasBody']["dc:publisher"]
            } for iiif_anno in annotation_set["images"]
        ]

        if isinstance(annotation_set['commentary'][0]['hasTarget'], list):
            result['orig_uri'] = annotation_set['commentary'][0]['hasTarget'][0]
            result['orig_text'] = annotation_set['commentary'][0]['hasTarget'][1]['chars']
        elif isinstance(annotation_set['commentary'][0]['hasTarget'], dict):
            result['orig_uri'] = ""
            result['orig_text'] = annotation_set['commentary'][0]['hasTarget']['chars']
        else:
            result['orig_uri'] = annotation_set['commentary'][0]['hasTarget']

        return result

    def validate_annotation(self, annotation):
        """Validate the structure of an annotation.

        This is not foolproof but it attempts to catch some errors that could come in from mistakes
        in data entry. It would be good to make sure these all couldn't occur to begin with.

        :param annotation: the annotation record
        :type annotation: dict

        :return: True if valid False if not
        :rtype: bool
        """
        try:
            if annotation['commentary'][0]['hasTarget'][0] != '':
                URN(annotation['commentary'][0]['hasTarget'][0])
        except ValueError:
            raise ValueError("Invalid commentary target - not parseable as URN")
        try:
            if isinstance(annotation['translation'][0]['hasBody'], str):
                URN(annotation['translation'][0]['hasBody'])
        except ValueError:
            raise ValueError("Invalid translation 1 uri - not parseable as URN")
        try:
            if isinstance(annotation['translation'][1]['hasBody'], str):
                URN(annotation['translation'][1]['hasBody'])
        except ValueError:
            raise ValueError("Invalid translation 2 uri - not parseable as URN")
        return True

    def retrieve_millietId_in_commentaries(self, commentaries):
        """ Extract a sorted list of Milliet ID from a set of commentary annotations

        :param commentaries: set of commentary annotations
        :type commentaries: list
        :return: sorted list of extracted Milliet numbers
        :rtype: list
        """
        millnum_list = []
        convert = lambda text: int(text) if text.isdigit() else text
        alphanum_key = lambda key: [convert(re.split('([A-Za-z]+)', key)[0])]
        for row in commentaries:
            try:
                cite_urn = str(row['commentary'][0]['hasBody']['@id'])
                millnum = cite_urn.split('.')[2]
                if millnum:
                    millnum_list.append(millnum)
                else:
                    pass
            except:
                pass
        return sorted(millnum_list, key=alphanum_key)

    def format_uri(self, milliet_id, subcollection_id=None):
        """ Make a Cite Collection URI for an annotation

        N.B. this is not a valid implementation of the CITE protocol, as it does not support
        CITE collections.  Future implementations should consider replacing this with a different identifier syntax.

        :param: milliet_id: The Milliet number
        :type: milliet_id: string
        :param: subcollection_id: the subcollection identifier (e.g. commentary, bibliography, etc.)
        :type: string

        :return:  the compiled URI
        :rtype: string
        """
        if subcollection_id is not None:
            return self.config['CITE_URI_PREFIX'] + self.config['CITE_COLLECTION'] + '.' + milliet_id + '.' + subcollection_id
        else:
            return self.config['CITE_URI_PREFIX'] + self.config['CITE_COLLECTION'] + '.' + milliet_id

    def format_person_from_authentificated_user(self):
        """ Make a Person for an annotation (i.e for contributor or creator)
        Uses the URI identifier for the user of the currently authenticated session

        :return: Person properties suitable for inclusion in the annotation
        :rtype: dict
        """
        person = self.auth.current_user()
        if person:
            return {
                "@id": person['uri'],
                "type": "Person",
                "name": person['name']
            }
        else:
            return None

    def update_contributors(self, annotation_dict=None):
        """ Update the contributors for an annotation

        Inserts a Person object for the currently authenticated user if she doesn't already appear
        as either creator or contributor.

        :param annotation_dict: the annotation to update
        :type annotation_dict: dict

        """
        if annotation_dict is None:
            annotation_dict = {}
        contributors = annotation_dict.setdefault('contributor',[])
        person = self.format_person_from_authentificated_user()
        if person:
            found = False
            for c in contributors:
                if c['@id'] == person['@id']:
                    found = True
                    break
            if not found:
                if 'creator' not in annotation_dict or annotation_dict['creator']['@id'] != person['@id']:
                    contributors.append(person)