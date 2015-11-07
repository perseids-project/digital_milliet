#!/usr/bin/python

from app import app
from flask import request, jsonify, url_for, session
import os, requests
from app import mongo
from bson.objectid import ObjectId

def author_db_build(auth=None):
	if auth is None:
		url = "http://catalog.perseus.org/cite-collections/api/authors/search?authority_name="
		dir_path = os.getcwd()
		list_path = dir_path + '/app/digmil_author_list.txt'
		auth_list = open(list_path, 'r')
		temp = auth_list.read().splitlines()
		
		for line in temp:		
			name_url = url + line.rstrip() + '&format=json'
			response_dict = requests.get(name_url).json()
			for resp in response_dict:
				author = {}
				obj = mongo.db.annotation.find_one({"cts_id" : resp['canonical_id']})
				if obj is None and resp['urn_status'] is not 'invalid':
					author['name'] = resp['authority_name']
					author['cts_id'] = resp['canonical_id']
					w_str = resp['related_works']
					author['works'] = []
					for cts in w_str.split(';'):
						if cts is not u'':
							w_url = "http://catalog.perseus.org/cite-collections/api/works/search?work=" + cts + "&format=json"
							w_response = requests.get(w_url).json()
							for w in w_response:
								work = {}
								try:
									work['cts_id'] = w['work']
									work['title'] = w['title_eng']
									author['works'].append(work)
								except TypeError, e:
									import pdb; pdb.set_trace()

					mongo.db.annotation.insert(author)


				else:
					pass

def process_comm(comm_list):
	millnum_list = []
	for row in comm_list:
		cite_urn = str(row['commentary'][0]['hasBody']['@id'])
		millnum = cite_urn.split('.')[2]
		if millnum:
			millnum_list.append(millnum)	
		else:
			pass
	return millnum_list

