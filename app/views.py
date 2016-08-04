# coding=utf8

from app import app
from flask import render_template, request, jsonify, flash, redirect, url_for, session
from os.path import expanduser
from app import mongo
import bson
from bson.objectid import ObjectId
from bson.json_util import dumps
from app import bower
from app.author_build import *
from app.data_parse import *
import re
import json

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
  if 'orig_uri' in parsed_obj:
    session['cts_uri'] = parsed_obj['orig_uri']

  return render_template('/commentary/commentary.html', obj=parsed_obj, info=auth_info)



@app.route('/edit/<millnum>')
def edit(millnum):
  parsed_obj, auth_info = get_it(millnum)

  return render_template('/commentary/edit.html', millnum=millnum, obj=parsed_obj)



@app.route('/edit/save_edit', methods = ['POST'])
def save_edit():
  form = request.form
  edit_save(form)

  return redirect('commentary')



#for catching requests from the perseids-client-apps form and saving the data
@app.route('/save_data', methods=['GET', 'POST'])
def save_data(): 
  millnum = save_from_form(request.args.to_dict(), HOME)
  
  return json.dumps({'millnum':millnum}, 200, {'ContentType':'application/json'})  


