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
	comm_list = mongo.db.annotation.find({}, {"commentary" : 1}).sort([("commentary.hasBody.@id" , 1)])
	millnum_list = []
	target_list = []
	for row in comm_list:
		cite_urn = str(row['commentary'][0]['hasBody']['@id'])
		target = str(row['commentary'][0]['hasTarget'])
		millnum = cite_urn.split('.')[2]
		if millnum:
			millnum_list.append(millnum)
			tup = (millnum, target)
			target_list.append(tup)
		else:
			pass
		
	auth_work_list = ""
	return render_template('commentary/list.html', millnum_list=millnum_list, auth_work_list=auth_work_list)

@app.route('/commentary/<millnum>')
def millnum(millnum):
	obj = mongo.db.annotation.find_one_or_404({"commentary.hasBody.@id" : "http://perseids.org/collections/urn:cite:perseus:digmil."+millnum+".c1"})
	parsed_obj = parse_it(obj)
	if parsed_obj.has_key('orig_uri'):
		session['cts_uri'] = parsed_obj['orig_uri']

	return render_template('/commentary/commentary.html', obj=parsed_obj)

@app.route('/edit/<millnum>')
def edit(millnum):
	obj = mongo.db.annotation.find_one_or_404({"commentary.hasBody.@id" : "http://perseids.org/collections/urn:cite:perseus:digmil."+millnum+".c1"})
	parsed_obj = parse_it(obj)
	return render_template('/commentary/edit.html', millnum=millnum, obj=parsed_obj)

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


	return result

def get_from_cite_coll(target_list):
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