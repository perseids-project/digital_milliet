#!/usr/bin/python

from flask import request, jsonify, url_for, session, flash
import os, requests, datetime
import re
from flask.ext.pymongo import PyMongo
from bson.objectid import ObjectId
from bson.json_util import dumps
import json


class Parser(object):

    def __init__(self,db=None,builder=None):
        self.mongo = db
        self.builder = builder


    def save_from_form(self,vals):
        json_data = self.make_json(vals)
        data = json.dumps(json_data, indent=2, sort_keys=True)
        raw_id = json_data['commentary'][0]['hasBody']['@id']
        mil_id = raw_id.split(':').pop()
        m_obj = self.add_to_db(json_data)
        if m_obj is not None:
            return mil_id.split('.')[1]
        else:
            return None

    def edit_save(self,form):
        record = self.mongo.db.annotation.find_one_or_404({'_id': ObjectId(form['mongo_id'])})
        record['commentary'][0]['hasBody']['chars'] = form['c1text']
        record['bibliography'][0]['hasBody']['chars'] = form['b1text']

        if 't1_text' in form:
            if form['t1_text'] != '':
                record['translation'][0]['hasBody']['chars'] = form['t1_text']
                record['translation'][0]['hasBody']['language'] = form['lang1']
        else:
            record['translation'][0]['hasBody'] = form['t1_uri']

        if 't2_text' in form:
            if form['t2_text'] != '':
                record['translation'][1]['hasBody']['chars'] = form['t2_text']
                record['translation'][1]['hasBody']['language'] = form['lang2']
        else:
              record['translation'][1]['hasBody'] = form['t2_uri']

        if 'orig_uri' in form:
              record['commentary'][0]['hasTarget'] = form['orig_uri']
        else:
              record['commentary'][0]['hasTarget']['chars'] = form['orig_text']

        if self.mongo.db.annotation.save(record):
              flash('Edit sucessfully saved')
        else:
              flash('Error!')



    def add_to_db(self,data_dict):
        #save data in mongo
        cid = data_dict["commentary"][0]["hasBody"]["@id"]
        exists = self.mongo.db.annotation.find_one({"commentary.hasBody.@id" : cid})
        m_obj = None
        if not exists:
            m_obj = self.mongo.db.annotation.insert(data_dict)
            #now compile author info
            self.builder.author_db_build(data_dict)
        return m_obj



    def make_json(self,vals):
        date = datetime.datetime.today()
        milnum = vals['milnum'].zfill(3)
        if vals['l1uri']:
            main_text = vals['l1uri']
        elif vals['own_uri_l1']:
            main_text = vals['own_uri_l1']
        else:
            main_text = dict(
                [("@id", "http://perseids.org/collections/urn:cite:perseus:digmil." + milnum+ ".l1"),
                 ("format", "text"),
                 ("chars", vals['l1text']),
                 ("language", vals['select_l1'])
                ])

        annotation = dict([
            ("commentary", [dict([
              ("@context", "http://www.w3.org/ns/oa-context-20130208.json"),
              ("@id", "digmilann." + str(self.uid(vals['c1text'], date))),
              ("@type", "oa:Annotation"),
              ("annotatedAt", str(date)),
              ("hasBody", dict([
                ("@id", "http://perseids.org/collections/urn:cite:perseus:digmil."+vals['milnum']+".c1"),
                ("format", "text"),
                ("chars", vals['c1text']),
                ("language", "eng")
              ])),
              ("hasTarget", main_text),
              ("motivatedBy", "oa:commenting")
            ])]),
            ("bibliography", [dict([
              ("@context", "http://www.w3.org/ns/oa-context-20130208.json"),
              ("@id", "digmilann." + str(self.uid(vals['b1text'], date))),
              ("@type", "oa:Annotation"),
              ("annotatedAt", str(date)),
              ("hasBody", dict([
                ("@id", "http://perseids.org/collections/urn:cite:perseus:digmil."+vals['milnum']+".b1"),
                ("format", "text"),
                ("chars", vals['b1text']),
                ("language", "eng")
              ])),
              ("hasTarget", "http://perseids.org/collections/urn:cite:perseus:digmil."+vals['milnum']+".c1"),
              ("motivatedBy", "oa:linking")
            ])]),
            ("translation", [dict([
              ("@context", "http://www.w3.org/ns/oa-context-20130208.json"),
              ("@id", "digmilann." + str(self.uid(vals['t1text'], date))),
              ("@type", "oa:Annotation"),
              ("annotatedAt", str(date)),
              ("hasBody", self.build_transl(self,"t1", vals['milnum'], vals['t1text'], vals['t1uri'], vals['own_uri_t1'], vals['select_t1'], vals['other_t1'])),
              ("hasTarget", main_text),
              ("motivatedBy", "oa:linking")
              ]),
              dict([
              ("@context", "http://www.w3.org/ns/oa-context-20130208.json"),
              ("@id", "digmilann." + str(self.uid(vals['t2text'], date))),
              ("@type", "oa:Annotation"),
              ("annotatedAt", str(date)),
              ("hasBody", self.build_transl(self,"t2", vals['milnum'], vals['t2text'], vals['t2uri'], vals['own_uri_t2'], vals['select_t2'], vals['other_t2'])),
              ("hasTarget", main_text),
              ("motivatedBy", "oa:linking")
              ])
            ]),
            ("tags", []),
            ("images", [])
        ])

        return annotation



    def uid(self,str, date):
        #creating unique ids based on a hash of the
        part1 = hash(str[0:4])
        mil = date.microsecond
        uid = part1 + mil
        return uid



    def build_transl(self,num, milnum, text, uri, own_uri, select, other):
        if not uri and not own_uri:
            if select is 'other' or other:
              lang = other
            else:
              lang = select

            body = dict([
              ("@id", "http://perseids.org/collections/urn:cite:perseus:digmil."+milnum+"."+num),
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
        obj = self.mongo.db.annotation.find_one_or_404({"commentary.hasBody.@id" : "http://perseids.org/collections/urn:cite:perseus:digmil."+millnum+".c1"})
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
        result = {}
        result['mid'] = obj['_id']
        result['bibl'] = obj['bibliography'][0]['hasBody']['chars']
        result['comm'] = obj['commentary'][0]['hasBody']['chars']
        for transl in obj['translation']:
            if (type(transl['hasBody']) is dict):
                t_num = transl['hasBody']['@id'].split('.')[-1]
                text = transl['hasBody']['chars']
                lang = transl['hasBody']['language']
                result[t_num+'_text'] = text
                result[t_num+'_lang'] = lang
            else:
                t_num = "t1"
                text = transl['hasBody']
                lang = re.search('\D+', text.split('-')[1]).group(0)
                result[t_num+'_uri'] = text
                result[t_num+'_lang'] = lang

            if (type(obj['commentary'][0]['hasTarget']) is dict):
                result['orig_text'] = obj['commentary'][0]['hasTarget']['chars']
            else:
                #import pdb; pdb.set_trace()
                result['orig_uri'] = obj['commentary'][0]['hasTarget']
                #uri_arr = obj['commentary'][0]['hasTarget'].split(':')
                #result['orig_text']= cts_retrieve(uri_arr)

        return result

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
