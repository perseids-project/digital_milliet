#!/usr/bin/python

import os, requests, datetime
from uuid import uuid4
import re, sys
from flask import session
from flask.ext.pymongo import PyMongo
from bson.objectid import ObjectId
from bson.json_util import dumps
import json
from MyCapytain.common.reference import URN


class Parser(object):
    """
    Parse Data for retrieva/storage to/from the database

       :param db Mongo Db Handle
       :type db PyMongo

       :param builder  helper for building new Author records
        :type builder AuthorBuilder

        :param config configuration dictionary
        :type config dict
    """

    def __init__(self,db=None,builder=None,config=None,auth=None):
        self.mongo = db
        self.builder = builder
        self.config = config
        self.auth = auth


    def save_from_form(self,vals):
        """
        Save a new set of annotations from the input form
        :param vals:
        :return: the nilliet number for the saved annotations or None if the record couldn't be saved
        """
        data = self.make_annotation(vals)
        raw_id = data['commentary'][0]['hasBody']['@id']
        mil_id = raw_id.split(':').pop()
        rv = None
        m_obj = self.add_to_db(data)
        if m_obj is not None:
            rv = mil_id.split('.')[1]
        return rv

    def edit_save(self,form):
        """
        Save an edited set of annotations to the db
        :param form:
        :return:  True if successful False if not
        """

        modtime = datetime.datetime.utcnow().isoformat()
        record = self.mongo.db.annotation.find_one_or_404({'_id': ObjectId(form['mongo_id'])})
        record['commentary'][0]['hasBody']['chars'] = form['c1text']
        record['bibliography'][0]['hasBody']['chars'] = form['b1text']
        cite_urn = record['commentary'][0]['hasBody']['@id']
        millnum = cite_urn.split('.')[2]


        if 't1_text' in form:
            if form['t1_text'] != '':
                if not record['translation'][0]['hasBody'] is dict:
                    # if we have switched from a uri to text then make sure we have the structure in place
                    record['translation'][0]['hasBody'] = self.build_transl("t1", millnum, form['t1_text'], None, None, form['lang1'])
                else:
                    record['translation'][0]['hasBody']['chars'] = form['t1_text']
                    record['translation'][0]['hasBody']['language'] = form['lang1']
        else:
            record['translation'][0]['hasBody'] = form['t1_uri']

        if 't2_text' in form:
            if form['t2_text'] != '':
                if not record['translation'][1]['hasBody'] is dict:
                    # if we have switched from a uri to text then make sure we have the structure in place
                    record['translation'][1]['hasBody'] = self.build_transl("t2", millnum, form['t2_text'], None, None, form['lang2'])
                else:
                    record['translation'][1]['hasBody']['chars'] = form['t2_text']
                    record['translation'][1]['hasBody']['language'] = form['lang2']
        else:
              record['translation'][1]['hasBody'] = form['t2_uri']

        record['commentary'][0]['modified'] = modtime
        record['bibliography'][0]['modified'] = modtime
        record['translation'][0]['modified'] = modtime
        record['translation'][1]['modified'] = modtime
        if (form['orig_uri'] != ''):
            record['translation'][0]['hasTarget'] = form['orig_uri']
            record['translation'][1]['hasTarget'] = form['orig_uri']
        self.update_contributors(record['commentary'][0])
        self.update_contributors(record['bibliography'][0])
        self.update_contributors(record['translation'][0])
        self.update_contributors(record['translation'][1])

        if (type(record['commentary'][0]['hasTarget']) is not list):
            main_text = dict(
                [("@id", self.make_uri(millnum,'l1')),
                 ("format", "text"),
                 ("chars", ""),
                 ("language", "")
                ])
            record['commentary'][0]['hasTarget'] = ["",main_text]
        record['commentary'][0]['hasTarget'][0] = form['orig_uri']
        record['commentary'][0]['hasTarget'][1]['chars'] = form['orig_text']
        record['commentary'][0]['hasTarget'][1]['language'] = form['orig_lang']

        rv =  None
        if self.validate_annotation(record):
            rv = self.mongo.db.annotation.save(record)
            self.builder.author_db_build(record)
        return rv


    def add_to_db(self,data_dict):
        """
         Add a new set of annotations ot the database
        :param data_dict:
        :return: the inserted db record or None if the record already existed
        """
        cid = data_dict["commentary"][0]["hasBody"]["@id"]
        exists = self.mongo.db.annotation.find_one({"commentary.hasBody.@id" : cid})
        m_obj = None
        if not exists and self.validate_annotation(data_dict):
            m_obj = self.mongo.db.annotation.insert(data_dict)
            #now compile author info
            self.builder.author_db_build(data_dict)
        return m_obj



    def make_annotation(self, vals):
        """
        Make a structure for the annotation from a set of key/value pairs
        :param vals:
        :return: the annotation as a JSON structure
        """
        date = datetime.datetime.today()
        milnum = vals['milnum'].zfill(3)
        person = self.make_person()
        primary_source_uri = ""
        if vals['l1uri']:
            primary_source_uri = vals['l1uri']
        elif vals['own_uri_l1']:
            primary_source_uri = vals['own_uri_l1']
        main_text = dict(
            [("@id", self.make_uri(milnum,'l1')),
             ("format", "text"),
             ("chars", vals['l1text']),
             ("language", vals['select_l1'])
            ])

        annotation = dict([
            ("commentary", [dict([
              ("@context", "http://www.w3.org/ns/oa-context-20130208.json"),
              ("@id", self.uid()),
              ("@type", "oa:Annotation"),
              ("annotatedAt", str(date)),
              ("creator",person),
              ("hasBody", dict([
                ("@id", self.make_uri(milnum,'c1')),
                ("format", "text"),
                ("chars", vals['c1text']),
                ("language", "eng")
              ])),
              ("hasTarget", [primary_source_uri,main_text]),
              ("motivatedBy", "oa:commenting")
            ])]),
            ("bibliography", [dict([
              ("@context", "http://www.w3.org/ns/oa-context-20130208.json"),
              ("@id", self.uid()),
              ("@type", "oa:Annotation"),
              ("annotatedAt", str(date)),
              ("creator",person),
              ("hasBody", dict([
                ("@id", self.make_uri(milnum,'b1')),
                ("format", "text"),
                ("chars", vals['b1text']),
                ("language", "eng")
              ])),
              ("hasTarget", self.make_uri(milnum,'c1')),
              ("motivatedBy", "oa:linking")
            ])]),
            ("translation", [dict([
              ("@context", "http://www.w3.org/ns/oa-context-20130208.json"),
              ("@id", self.uid()),
              ("@type", "oa:Annotation"),
              ("annotatedAt", str(date)),
              ("creator",person),
              ("hasBody", self.build_transl("t1", vals['milnum'], vals['t1text'], vals['t1uri'], vals['own_uri_t1'], vals['lang_t1'])),
              ("hasTarget", primary_source_uri),
              ("motivatedBy", "oa:linking")
              ]),
              dict([
              ("@context", "http://www.w3.org/ns/oa-context-20130208.json"),
              ("@id", self.uid()),
              ("@type", "oa:Annotation"),
              ("annotatedAt", str(date)),
              ("creator",person),
              ("hasBody", self.build_transl("t2", vals['milnum'], vals['t2text'], vals['t2uri'], vals['own_uri_t2'], vals['lang_t2'])),
              ("hasTarget", primary_source_uri),
              ("motivatedBy", "oa:linking")
              ])
            ]),
            ("tags", []),
            ("images", [])
        ])
        return annotation



    def uid(self):
        """
        Create a unique id for an annotation
        :return: uid
        """
        uuid = 'digmilann.' + str(uuid4())
        return uuid



    def build_transl(self,num, milnum, text, uri, own_uri, lang):
        """
        Build the body of a translation annotation
        :param num:
        :param milnum:
        :param text:
        :param uri:
        :param own_uri:
        :param lang:
        :return: the body of the translation annotation
        """
        if not uri and not own_uri:
            body = dict([
              ("@id", self.make_uri(milnum,num)),
              ("format", "text"),
              ("chars", text),
              ("language", lang)
            ])
        elif not uri and own_uri:
            body = own_uri
        else:
            body = uri

        return body



    def get_it(self,millnum):
        """
        Get the first set of annotations that target the supplied Milliet Number
        :param millnum:  Milliet Number
        :return: the annotation set as a dict
        """
        obj = self.mongo.db.annotation.find_one_or_404({"commentary.hasBody.@id" : self.make_uri(millnum,'c1')})
        parsed_obj = self.parse_it(obj)
        info = self.mongo.db.annotation.find_one({'works.millnums' : {'$elemMatch':  {'$elemMatch' :{'$in': [millnum]}}}})
        auth_info = {}
        if info is None:
            auth_info['auth'] = ""
            auth_info['work'] = ""
            auth_info['passage'] = ""
        else:
            auth_info['auth'] = info['name']
            for w in info['works']:
                for tup in w['millnums']:
                    if millnum in tup:
                        auth_info['work'] = w['title']
                        auth_info['passage'] = tup[1]

        return parsed_obj, auth_info



    def parse_it(self,obj):
        """
        Parse a db record into a dict
        :param obj: the db record
        :return:  parsed as a dict
        """
        result = {}
        result['mid'] = obj['_id']
        result['bibl'] = obj['bibliography'][0]['hasBody']['chars']
        result['comm'] = obj['commentary'][0]['hasBody']['chars']
        if 'creator' in obj['commentary'][0]:
            result['creator'] = obj['commentary'][0]['creator']
        else:
            result['creator'] = None
        if 'contributor' in obj['commentary'][0]:
            result['contributor'] = obj['commentary'][0]['contributor']
        else:
            result['contributor'] = None
        tnum = 0
        for transl in obj['translation']:
            tnum = tnum + 1
            if (type(transl['hasBody']) is dict):
                t_num = transl['hasBody']['@id'].split('.')[-1]
                text = transl['hasBody']['chars']
                lang = transl['hasBody']['language']
                result[t_num+'_text'] = text
                result[t_num+'_lang'] = lang
            else:
                t_num = "t" + str(tnum)
                text = transl['hasBody']
                try:
                    urn = URN(text)
                    lang = re.search('\D+', text.split('-')[1]).group(0)
                    result[t_num+'_uri'] = text
                    result[t_num+'_lang'] = lang
                except:
                    # invalid URN we need to recover
                    result[t_num+'_text'] = text
                    result[t_num+'_lang'] = "eng"
                    pass
        if (type(obj['commentary'][0]['hasTarget']) is list):
            result['orig_uri'] = obj['commentary'][0]['hasTarget'][0]
            result['orig_text'] = obj['commentary'][0]['hasTarget'][1]['chars']
        elif (type(obj['commentary'][0]['hasTarget']) is dict):
            result['orig_uri'] = ""
            result['orig_text'] = obj['commentary'][0]['hasTarget']['chars']
        else:
            result['orig_uri'] = obj['commentary'][0]['hasTarget']

        return result

    def validate_annotation(self,annotation):
        """
        Validate the structure of an annotation.

        This is not foolproof but it attempts to catch some errors that could come in from mistakes
        in data entry. It would be good to make sure these all couldn't occur to begin with.
        :return: True if valid False if not
        """
        try:
            if (annotation['commentary'][0]['hasTarget'][0] != ''):
                urn = URN(annotation['commentary'][0]['hasTarget'][0])
        except ValueError as err:
            raise ValueError("Invalid commentary target - not parseable as URN")
        try:
            if isinstance(annotation['translation'][0]['hasBody'],str):
                urn = URN(annotation['translation'][0]['hasBody'])
        except ValueError as err:
            raise ValueError("Invalid translation 1 uri - not parseable as URN")
        try:
            if isinstance(annotation['translation'][1]['hasBody'],str):
                urn = URN(annotation['translation'][1]['hasBody'])
        except ValueError as err:
            raise ValueError("Invalid translation 2 uri - not parseable as URN")
        return True


    def process_comm(self,comm_list):
        """
        Extract a sorted list of milliet numbers from a set of commentary annotations
        :param comm_list: set of commentary annotations
        :return: sorted list of milliet numbers
        """
        millnum_list = []
        convert = lambda text: int(text) if text.isdigit() else text
        alphanum_key = lambda key: [ convert(re.split('([A-Za-z]+)', key)[0]) ]
        for row in comm_list:
            try:
                cite_urn = str(row['commentary'][0]['hasBody']['@id'])
                millnum = cite_urn.split('.')[2]
                if millnum:
                    millnum_list.append(millnum)
                else:
                    pass
            except:
                pass
        return sorted(millnum_list,key=alphanum_key)

    def make_uri(self, milnum, subcoll):
        """
        Make a URI for an annotation
        :return:  uri
        """
        return self.config['CITE_URI_PREFIX'] +  self.config['CITE_COLLECTION'] + '.' + milnum + '.' + subcoll

    def make_person(self):
        """
        Make a person for an annotation (i.e for contributor or creator)
        :return: a dict with the person attributes
        """
        person = self.auth.current_user()
        if person:
            return dict([
                ("id", person['uri']),
                ("type", "Person"),
                ("name", person['name'])
            ])
        else:
            return None

    def update_contributors(self,annotation_dict=dict):
        """
        Update the contributors for an annotation
        :param annotation_dict: the annotation to update
        :return: None - annotation updated in place
        """
        contributors = annotation_dict.setdefault('contributor',[])
        person = self.make_person()
        if person:
            found = False
            for c in contributors:
                if c['id'] == person['id'] :
                    found = True
                    break
            if not found:
                if 'creator' in annotation_dict and annotation_dict['creator']['id'] != person['id']:
                    contributors.append(person)

    #This and the commented out lines above in parse_it and the commented out imports are for the new CTS service
    #using MyCapytains to access it. For now, since there are not as many texts that are CTS/TEI compliant
    #meaning we lose access to texts with the switch, the javascript call in commentary.js will have to do.
    def cts_retrieve(self,uri_arr):
        orig_uri = ":".join(uri_arr[:4])
        cts = cts5.CTS('http://cts.perseids.org/api/cts/', inventory="digmill")
        text = Text(orig_uri, cts)
        ref = reference.Reference(reference = uri_arr[4])
        try:
            passg = text.getPassage(ref)
        except IndexError:
            passg = ""

        return passg



    def get_from_cite_coll(self,target_list):
        a_addr = "http://catalog.perseus.org/cite-collections/api/authors/search?"
        w_addr = "http://catalog.perseus.org/cite-collections/api/works/search?"
        #this isn't finished!! need to pull info out of the target list and batch send the urns to the cite collections
        #then need to match it all back up again?S
        if auth in auth_work_list:
            if work in auth_work_list[auth]:
                pass
            else:
                auth_work_list[auth].append(work).sort()
        else:
            auth_work_list[auth] = [work]
