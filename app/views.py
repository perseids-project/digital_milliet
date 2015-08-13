# coding=utf8

from app import app
from flask import render_template, request, jsonify, flash, redirect, url_for, session
from os.path import expanduser
from app import mongo
from app import bower
import re

HOME = expanduser("~")
app.secret_key = 'adding this in so flash messages will work'

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/commentary')
def commentary():
	comm_list = mongo.db.annotation.find({}, {"commentary.hasBody.@id" : 1}).sort([("commentary.hasBody.@id" , 1)])
	millnum_list = []
	for row in comm_list:
		cite_urn = str(row['commentary'][0]['hasBody']['@id'])
		millnum = cite_urn.split('.')[2]
		if millnum:
			millnum_list.append(millnum)
		else:
			pass

	return render_template('commentary/list.html', millnum_list=millnum_list)

@app.route('/commentary/<millnum>')
def millnum(millnum):
	obj = mongo.db.annotation.find_one_or_404({"commentary.hasBody.@id" : "http://perseids.org/collections/urn:cite:perseus:digmil."+millnum+".c1"})
	parsed_obj = parse_it(obj)
	return render_template('/commentary/commentary.html', obj=parsed_obj)


def parse_it(obj):	
	result = {}
	result['bibl'] = obj['bibliography'][0]['hasBody']['chars']
	result['comm'] = obj['commentary'][0]['hasBody']['chars']
	for transl in obj['translation']:
		if (type(transl['hasBody']) is dict):
			text = transl['hasBody']['chars']
			lang = transl['hasBody']['language']
			result[lang+'_text'] = text
		else:
			text = transl['hasBody']
			lang = re.search('\D+', text.split('-')[1]).group(0)
			result[lang+'_uri'] = text

	if (type(obj['commentary'][0]['hasTarget']) is dict):
		result['orig_text'] = obj['commentary'][0]['hasTarget']['chars']
	else:
		result['orig_uri'] = obj['commentary'][0]['hasTarget']


	import pdb; pdb.set_trace()
	return result
