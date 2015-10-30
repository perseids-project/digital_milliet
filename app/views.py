# coding=utf8

from app import app
from flask import render_template, request, jsonify, flash, redirect, url_for, session
from os.path import expanduser
from app import mongo
from bson.objectid import ObjectId
from app import bower
import re

HOME = expanduser("~")
app.secret_key = 'adding this in so flash messages will work'

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/about')
def about():
	return render_template('about.html')

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
	parsed_obj = get_it(millnum)
	if parsed_obj.has_key('orig_uri'):
		session['cts_uri'] = parsed_obj['orig_uri']

	return render_template('/commentary/commentary.html', obj=parsed_obj)

@app.route('/edit/<millnum>')
def edit(millnum):
	parsed_obj = get_it(millnum)
	return render_template('/commentary/edit.html', millnum=millnum, obj=parsed_obj)


@app.route('/save_edit', methods = ['POST'])
def save_edit():
	form = request.form
	#could do wholesale replace of document but then might risk losing the tags or images
	record = mongo.db.annotation.find_one_or_404({'_id': ObjectId(form['mongo_id'])})
	record['commentary'][0]['hasBody']['chars'] = form['c1text']
	record['bibliography'][0]['hasBody']['chars'] = form['b1text']
	#translations need to find correct language and account for uri or char body
	if ((type(record['translation'][0]['hasBody']) is dict) and record['translation'][0]['hasBody']['language'] == 'eng') or re.search('eng', record['translation'][0]['hasBody']):
		transl_eng = record['translation'][0]
		transl_fra = record['translation'][1]
	else:
		transl_eng = record['translation'][1]
		transl_fra = record['translation'][0]
	
	if 'eng_text' in form:
		transl_eng['hasBody']['chars'] = form['eng_text']
	else:
		transl_eng['hasBody'] = form['eng_uri']
	
	if 'fra_text' in form:
		transl_fra['hasBody']['chars'] = form['fra_text']
	else:
		transl_fra['hasBody'] = form['fra_uri']
	
	if 'orig_uri' in form:
		record['commentary'][0]['hasTarget'] = form['orig_uri']
	else:
		record['commentary'][0]['hasTarget']['chars'] = form['orig_text']
	
	if mongo.db.annotation.save(record):
		flash('Edit sucessfully saved')
	else:
		flash('Error!')

	return redirect('/commentary')




def get_it(millnum):
	obj = mongo.db.annotation.find_one_or_404({"commentary.hasBody.@id" : "http://perseids.org/collections/urn:cite:perseus:digmil."+millnum+".c1"})
	parsed_obj = parse_it(obj)
	return parsed_obj


def parse_it(obj):	
	result = {}
	result['mid'] = obj['_id']
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