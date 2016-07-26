#!/usr/bin/python

from app import app
from flask import request, jsonify, url_for, session
import os, requests, datetime
import re
from app import mongo
from bson.objectid import ObjectId
import json
from app.author_build import *

def save_from_form(vals, HOME):
  import pdb; pdb.set_trace()
  json_data = make_json(vals)
  data = json.dumps(json_data, indent=2, sort_keys=True)
  raw_id = json_data['commentary'][0]['hasBody']['@id']
  m_obj = add_to_db(json_data)
  mil_id = raw_id.split(':').pop()
  path = "/digmil/"+mil_id+".txt"
  session['path'] = path
  session['obj'] = str(m_obj)  
  with open(HOME+path, "wb") as mil_file:
    mil_file.write(data)

  return path, data



def add_to_db(data_dict):
  #save data in mongo
  m_obj = mongo.db.annotation.insert(data_dict)  
  #now compile author info
  author_db_build(data_dict)
  
  return m_obj


def make_json(vals):
  date = datetime.datetime.today()
  milnum = vals['milnum'].zfill(3)
  if not vals['l1uri']:
    if not vals['own_uri_l1']:
      main_text = dict(
        [("@id", "http://perseids.org/collections/urn:cite:perseus:digmil." + milum+ ".l1"),
        ("format", "text"),
        ("chars", vals['l1text']),
        ("language", vals['select_l1'])
        ])
    else:
      main_text = vals['own_uri_l1']
  else:
    main_text = vals['l1uri']
  
  annotation = dict([
    ("commentary", [dict([
      ("@context", "http://www.w3.org/ns/oa-context-20130208.json"),
      ("@id", "digmilann." + str(uid(vals['c1text'], date))),
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
      ("@id", "digmilann." + str(uid(vals['b1text'], date))),
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
      ("@id", "digmilann." + str(uid(vals['t1text'], date))), 
      ("@type", "oa:Annotation"),
      ("annotatedAt", str(date)),        
      ("hasBody", build_transl("t1", vals['milnum'], vals['t1text'], vals['t1uri'], vals['own_uri_t1'], vals['select_t1'], vals['other_t1'])),
      ("hasTarget", main_text),
      ("motivatedBy", "oa:linking")
      ]),
      dict([
      ("@context", "http://www.w3.org/ns/oa-context-20130208.json"),
      ("@id", "digmilann." + str(uid(vals['t2text'], date))),
      ("@type", "oa:Annotation"),
      ("annotatedAt", str(date)),
      ("hasBody", build_transl("t2", vals['milnum'], vals['t2text'], vals['t2uri'], vals['own_uri_t2'], vals['select_t2'], vals['other_t2'])),
      ("hasTarget", main_text),
      ("motivatedBy", "oa:linking")
      ])
    ]),
    ("tags", []),
    ("images", [])
  ])
  
  return annotation



def uid(str, date):
  #creating unique ids based on a hash of the 
  part1 = hash(str[0:4])
  mil = date.microsecond
  uid = part1 + mil
  return uid



def build_transl(num, milnum, text, uri, own_uri, select, other):
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

{'commentary': [{'motivatedBy': 'oa:commenting', 'hasTarget': 'urn:cts:latinLit:phi1056.phi001.perseus-lat1:1.1.1-1.1.1', '@context': 'http://www.w3.org/ns/oa-context-20130208.json', '@type': 'oa:Annotation', 'hasBody': {'format': 'text', '@id': 'http://perseids.org/collections/urn:cite:perseus:digmil.23456789.c1', 'chars': 'wqdewfresgtrdhytjukilo', 'language': 'eng'}, 'annotatedAt': '2016-07-26 16:11:42.485480', '@id': 'digmilann.5965983798380217224'}], '_id': ObjectId('5797c403fcfb727347e866c6'), 'images': [], 'translation': [{'motivatedBy': 'oa:linking', 'hasTarget': 'urn:cts:latinLit:phi1056.phi001.perseus-lat1:1.1.1-1.1.1', '@context': 'http://www.w3.org/ns/oa-context-20130208.json', '@type': 'oa:Annotation', 'hasBody': 'urn:cts:latinLit:phi1056.phi001.perseus-eng1:1.1.1-1.1.1', 'annotatedAt': '2016-07-26 16:11:42.485480', '@id': 'digmilann.1360570924997549291'}, {'motivatedBy': 'oa:linking', 'hasTarget': 'urn:cts:latinLit:phi1056.phi001.perseus-lat1:1.1.1-1.1.1', '@context': 'http://www.w3.org/ns/oa-context-20130208.json', '@type': 'oa:Annotation', 'hasBody': {'format': 'text', '@id': 'http://perseids.org/collections/urn:cite:perseus:digmil.23456789.t2', 'chars': 'qwdefegthryjtukiyujyhgfds"', 'language': 'fra'}, 'annotatedAt': '2016-07-26 16:11:42.485480', '@id': 'digmilann.-4441570331895779802'}], 'tags': [], 'bibliography': [{'motivatedBy': 'oa:linking', 'hasTarget': 'http://perseids.org/collections/urn:cite:perseus:digmil.23456789.c1', '@context': 'http://www.w3.org/ns/oa-context-20130208.json', '@type': 'oa:Annotation', 'hasBody': {'format': 'text', '@id': 'http://perseids.org/collections/urn:cite:perseus:digmil.23456789.b1', 'chars': 'weafrethdytjuykilo', 'language': 'eng'}, 'annotatedAt': '2016-07-26 16:11:42.485480', '@id': 'digmilann.-7543811096773959574'}]}
