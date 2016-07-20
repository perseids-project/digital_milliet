#!/usr/bin/python

from app import app
from flask import request, jsonify, url_for, session
import os, requests
import re
from app import mongo
from bson.objectid import ObjectId

#!! All of this needs to be converted out of JS to Python !!

# function make_json(vals){
#   var date = new Date();
#   var milnum = ('000' + vals['milnum']).slice(-3)
#   if (vals['l1uri'] == ""){
#     if (vals['own_uri_l1'] == ""){
#       var main_text = {
#         "@id" : "http://perseids.org/collections/urn:cite:perseus:digmil."+milnum+".l1",
#         "format" : "text",
#         "chars" : vals['l1text'],
#         "language" : vals['select_l1']
#       };
#     } else {
#       var main_text = vals['own_uri_l1'];
#     }
#   }else{ 
#     var main_text = vals['l1uri'];
#   } 
   
#   var annotation = {
#     commentary : [
#       {  
#         "@context": "http://www.w3.org/ns/oa-context-20130208.json", 
#         "@id": "digmilann." + uid(vals['c1text'], date), 
#         "@type": "oa:Annotation",
#         "annotatedAt": date,
        
#         "hasBody": {
#           "@id" : "http://perseids.org/collections/urn:cite:perseus:digmil."+vals['milnum']+".c1",
#           "format" : "text",
#           "chars" : vals['c1text'],
#           "language" : "eng"
#         },
#         "hasTarget":  main_text,
#         "motivatedBy": "oa:commenting"
#       }
#     ],
#     bibliography : [ 
#       {
#         "@context": "http://www.w3.org/ns/oa-context-20130208.json", 
#         "@id": "digmilann." + uid(vals['b1text'], date), 
#         "@type": "oa:Annotation",
#         "annotatedAt": date, 

#         "hasBody":{
#           "@id" : "http://perseids.org/collections/urn:cite:perseus:digmil."+vals['milnum']+".b1",
#           "format" : "text",
#           "chars" : vals['b1text'],
#           "language" : "eng"
#         },
#         "hasTarget": "http://perseids.org/collections/urn:cite:perseus:digmil."+vals['milnum']+".c1",
#         "motivatedBy": "oa:linking"
#       }
#     ],
#     translation : [
#       {
#         "@context": "http://www.w3.org/ns/oa-context-20130208.json", 
#         "@id": "digmilann." + uid(vals['t1text'], date), 
#         "@type": "oa:Annotation",
#         "annotatedAt": date,
        
#         "hasBody": build_transl("t1", vals['milnum'], vals['t1text'], vals['t1uri'], vals['own_uri_t1'], vals['select_t1'], vals['other_t1']),
#         "hasTarget": main_text,
#         "motivatedBy": "oa:linking"
#       },
#       {
#         "@context": "http://www.w3.org/ns/oa-context-20130208.json", 
#         "@id": "digmilann." + uid(vals['t2text'], date), 
#         "@type": "oa:Annotation",
#         "annotatedAt": date,
        
#         "hasBody": build_transl("t2", vals['milnum'], vals['t2text'], vals['t2uri'], vals['own_uri_t2'], vals['select_t2'], vals['other_t2']),
#         "hasTarget": main_text,
#         "motivatedBy": "oa:linking"
#       }
#     ],
#     tags : [],
#     images : []
#   };
#   return annotation;
# }

# function uid(str, date) {
#   String.prototype.hashCode = function() {
#     var hash = 0, i, chr, len;
#     if (this.length == 0) return hash;
#     for (i = 0, len = this.length; i < len; i++) {
#       chr   = this.charCodeAt(i);
#       hash  = ((hash << 5) - hash) + chr;
#     }
#     return hash;
#   };

#   var h = str.hashCode();
#   var part1 = h.toString().substr(0,4);
#   var mil = date.getMilliseconds().toString();
#   var uid = part1 + mil;

#   return uid;
# }

# function build_transl(num, milnum, text, uri, own_uri, select, other){

#   if (uri == "" && own_uri == ""){
#     if (select == 'other' || !(other == "")) {
#         var lang = other;
#     } else {
#        var lang = select;
#     }
#     var body = {
#       "@id" : "http://perseids.org/collections/urn:cite:perseus:digmil."+milnum+"."+num,
#       "format" : "text",
#       "chars" : text,
#       "language" : lang
#     };
#   } else if (uri == "" && !(own_uri == "")){
#     var body = own_uri;
#   }else{
#     var body = uri;
#   }
#   return body;
# }

