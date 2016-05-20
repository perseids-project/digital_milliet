# coding=utf8

from app import app
from flask import render_template, request, jsonify, flash, redirect, url_for, session
from os.path import expanduser
from app import mongo
from bson.objectid import ObjectId
from app import bower
from author_build import *
from app import markdown
#from MyCapytain.endpoints import cts5
#from MyCapytain.resources.texts.api import Text
#from MyCapytain.common import reference
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

@app.route('/search', methods = ['POST'])
def search():
	form = request.form
	if form['dropdown'] == "Author":
		res = mongo.db.annotation.find({"name" : form['value']})
	else:
		res = mongo.db.annotation.find({"works.title" : form['value']})

	if res.count() == 0:
		res = None

	return render_template('search.html', res = res)

@app.route('/commentary')
def commentary():
	#add_to_existing_db()
	comm_list = mongo.db.annotation.find({"commentary" : {'$exists' : 1}}).sort([("commentary.hasBody.@id" , 1)])
	auth_list = mongo.db.annotation.find({"cts_id" : {'$exists' : 1}}).sort([("name" , 1)])
	millnum_list = process_comm(comm_list)
	return render_template('commentary/list.html', millnum_list=millnum_list, auth_list=auth_list)

@app.route('/commentary/<millnum>')
def millnum(millnum):
	parsed_obj, auth_info = get_it(millnum)
	if parsed_obj.has_key('orig_uri'):
		session['cts_uri'] = parsed_obj['orig_uri']

	return render_template('/commentary/commentary.html', obj=parsed_obj, info=auth_info)

@app.route('/edit/<millnum>')
def edit(millnum):
	parsed_obj, auth_info = get_it(millnum)
	return render_template('/commentary/edit.html', millnum=millnum, obj=parsed_obj)


@app.route('/edit/save_edit', methods = ['POST'])
def save_edit():
	form = request.form
	#could do wholesale replace of document but then might risk losing the tags or images
	record = mongo.db.annotation.find_one_or_404({'_id': ObjectId(form['mongo_id'])})
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
	
	if mongo.db.annotation.save(record):
		flash('Edit sucessfully saved')
	else:
		flash('Error!')

	return redirect('commentary')




def get_it(millnum):
	obj = mongo.db.annotation.find_one_or_404({"commentary.hasBody.@id" : "http://perseids.org/collections/urn:cite:perseus:digmil."+millnum+".c1"})
	parsed_obj = parse_it(obj)
	info = mongo.db.annotation.find_one({'works.millnums' : {'$elemMatch':  {'$elemMatch' :{'$in': [millnum]}}}})
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


def parse_it(obj):	
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
                        t_num = "1" 
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

#This and the commented out lines above in parse_it and the commented out imports are for the new CTS service
#using MyCapytains to access it. For now, since there are not as many texts that are CTS/TEI compliant
#meaning we lose access to texts with the switch, the javascript call in commentary.js will have to do.
def cts_retrieve(uri_arr):
	orig_uri = ":".join(uri_arr[:4])
	cts = cts5.CTS('http://cts.perseids.org/api/cts/', inventory="digmill")
	text = Text(orig_uri, cts)
	ref = reference.Reference(reference = uri_arr[4])
	try:
		passg = text.getPassage(ref)
	except IndexError:
		passg = ""

	return passg


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
