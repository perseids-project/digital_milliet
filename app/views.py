# coding=utf8

from app import app
from flask import render_template, request, jsonify, flash, redirect, url_for, session
from os.path import expanduser
from app import mongo

HOME = expanduser("~")
app.secret_key = 'adding this in so flash messages will work'

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/commentary')
def commentary():
	comm_list = mongo.db.find({}, {"commentary.hasBody.@id" : 1})
	return render_template('commentary/list.html')

@app.route('/commentary/<millnum>')
def millnum(millnum):
	obj = mongo.db.annotation.find_one_or_404({"commentary.hasBody.@id" : "http://perseids.org/collections/urn:cite:perseus:digmil."+millnum+".c1"})
	return render_template('/commentary/commentary.html', obj)