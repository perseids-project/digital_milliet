#!/usr/bin/python

from app import app
from flask import request, jsonify, url_for, session
import os, requests, datetime
import re
from app import mongo
from bson.objectid import ObjectId
import json


def make_json(vals):
	date = datetime.today()
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
			("@context" "http://www.w3.org/ns/oa-context-20130208.json"),
			("@id", "digmilann." + uid(vals['c1text'], date)),
			("@type", "oa:Annotation"),
			("annotatedAt", date),
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
			("@id", "digmilann." + uid(vals['b1text'], date)),
			("@type", "oa:Annotation"),
			("annotatedAt", date),
			("hasBody", dict([
				("@id", "http://perseids.org/collections/urn:cite:perseus:digmil."+vals['milnum']+".b1"),
				("format", "text"),
        ("chars", vals['b1text']),
        ("language", "eng")
			])),
			("hasTarget", "http://perseids.org/collections/urn:cite:perseus:digmil."+vals['milnum']+".c1"),
      ("motivatedBy", "oa:linking")
		])]),
		(translation, [dict([
			("@context", "http://www.w3.org/ns/oa-context-20130208.json"), 
      ("@id", "digmilann." + uid(vals['t1text'], date)), 
      ("@type", "oa:Annotation"),
      ("annotatedAt", date),        
      ("hasBody", build_transl("t1", vals['milnum'], vals['t1text'], vals['t1uri'], vals['own_uri_t1'], vals['select_t1'], vals['other_t1'])),
      ("hasTarget", main_text),
      ("motivatedBy", "oa:linking")
			]),
			dict([
			("@context", "http://www.w3.org/ns/oa-context-20130208.json"),
			("@id", "digmilann." + uid(vals['t2text'], date)),
			("@type", "oa:Annotation"),
			("annotatedAt", date),
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

