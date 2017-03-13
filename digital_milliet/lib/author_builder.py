#!/usr/bin/python

from flask import request, jsonify, url_for, session
import os, requests
import re
from MyCapytain.common.reference import URN
from bson.objectid import ObjectId

class AuthorBuilder(object):
    """
      Provides methods for building new Author records in the database

       :param db Mongo Db Handle
       :type db PyMongo
       :param catalog Catalog API Manager
       :type catalog Catalog
    """

    def __init__(self, db=None, catalog=None):
        self.mongo = db
        self.catalog = catalog

    def author_db_build(self,data_dict):
        """
        Adds or Updates Author Records in the Annotation Database
        Author Records contain authority name  and work information
        and are populated as annotations referencing an author and work
        are added to the annotator store so that they can be used for browsing

        :param data_dict: the full annotation
        :type data_dict dict of the annotation
        :return: None
        """
        try:
            target = data_dict['commentary'][0]['hasTarget']
            cite_urn = data_dict['commentary'][0]['hasBody']['@id']
            if (type(target) is str):
                urn = URN(target)
                millnum = cite_urn.split('.')[2]
                t_parts = target.split(':')
                urn_parts = t_parts[3].split('.')
                pasg = t_parts[4]
                auth_id = urn_parts[0]
                work_id = ':'.join(t_parts[0:3]) + ':' + '.'.join(urn_parts[0:2])


            author = self.mongo.db.annotation.find_one({"cts_id" : auth_id})
            if author is None:
                response_dict = self.catalog.lookup_author(auth_id)
                for resp in response_dict:
                    if resp['urn_status'] is not 'invalid':
                        author = self.make_author(resp)

            works = author['works']
            if not works:
                works.append(self.make_work(work_id, millnum, pasg))
            else:
                work = next((ent for ent in works if ent['cts_id'] == work_id), None)
                if work is None:
                    works.append(self.make_work(work_id, millnum, pasg))
                else:
                    if millnum not in work['millnums']:
                        l = [millnum, pasg]
                        work['millnums'].append(l)

            self.mongo.db.annotation.update({'_id' : author['_id']}, author)
        except TypeError:
            pass
        except KeyError:
            pass
        except ValueError:
            pass
        except:
            pass

    def make_author(self,resp):
        """
        Make an author from a catalog record and insert it in the database
        :param millnum:
        :param pasg:
        :return:
        """
        author = {}
        author['name'] = resp['authority_name']
        author['cts_id'] = resp['canonical_id']
        author['works'] = []
        a_id = self.mongo.db.annotation.insert(author)
        new_auth = self.mongo.db.annotation.find_one({'_id' : a_id})
        return new_auth


    def make_work(self,work_id, millnum, pasg):
        """
        Make a work from a catalog record
        :param millnum:
        :param pasg:
        :return:
        """
        w_resp = self.catalog.lookup_work(work_id)
        for w in w_resp:
            if w['urn_status'] is not 'invalid':
                work = {}
                work['title'] = w['title_eng']
                work['cts_id'] = w['work']
                l = [[millnum, pasg]]
                work['millnums'] = l
        return work

    def process_comm(self,comm_list):
        """
        Extract a sorted list of milliet numbers from a set of commentary annotations
        :param comm_list: set of commentary annotations
        :return: sorted list of milliet numbers
        """
        millnum_list = []
        convert = lambda text: int(text) if text.isdigit() else text
        alphanum_key = lambda key: [ convert(re.split('([A-Za-z]+)', key)[0]) ]
        for row in comm_list:
            try:
                cite_urn = str(row['commentary'][0]['hasBody']['@id'])
                millnum = cite_urn.split('.')[2]
                if millnum:
                    millnum_list.append(millnum)
                else:
                    pass
            except:
                pass
        return sorted(millnum_list,key=alphanum_key)
