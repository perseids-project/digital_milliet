#!/usr/bin/python

from flask import request, jsonify, url_for, session
import os, requests
import re
from MyCapytain.common.reference import URN
from bson.objectid import ObjectId

class AuthorBuilder(object):
    """ Provides methods for building new Author records in the database
    """

    def __init__(self, db=None, catalog=None):
        """ Constructor

        :param db: Mongo Db Handle
        :type db: PyMongo
        :param catalog: Catalog API Manager
        :type catalog: Catalog
        """
        self.mongo = db
        self.catalog = catalog

    def author_db_build(self,data_dict):
        """ Adds or Updates Author Records in the Annotation Database

        Author Records contain authority name  and work information
        and are populated as annotations referencing an author and work
        are added to the annotator store so that they can be used for browsing

        :param data_dict: the full annotation
        :type data_dict: dict

        """
        try:
            target = data_dict['commentary'][0]['hasTarget'][0]
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

            # we may still not have an author here, if the catalog lookup didn't succeed
            if author is not None:
                works = author['works']
                if not works:
                    works.append(self.make_work(work_id, millnum, pasg))
                else:
                    work = next((ent for ent in works if 'cts_id' in ent and ent['cts_id'] == work_id), None)
                    if work is None:
                        works.append(self.make_work(work_id, millnum, pasg))
                    else:
                        if millnum not in work['millnums']:
                            l = [millnum, pasg]
                            work['millnums'].append(l)

                self.mongo.db.annotation.update({'_id' : author['_id']}, author)
            else:
                print("Unable to get catalog info for " + target)
        except TypeError as err:
            print("Invalid data for author build",err)
            pass
        except KeyError as err:
            print("Invalid data for author build",err)
            pass
        except ValueError as err:
            print("Invalid data for author build",err)
            pass
        except:
            print("Invalid data for author build")
            pass

    def author_millnum_get(self,millnum):
        """ Get an author record for a milliet number

        :param millnum: the milliet number to remove
        :type millnum: string

        """
        return self.mongo.db.annotation.find_one({'works.millnums' : {'$elemMatch':  {'$elemMatch' :{'$in': [millnum]}}}})

    def author_millnum_remove(self,millnum):
        """ Remove a milliet number mapping from an author record

        :param millnum: the milliet number to remove
        :type millnum: string

        """
        info = self.mongo.db.annotation.find_one({'works.millnums' : {'$elemMatch':  {'$elemMatch' :{'$in': [millnum]}}}})
        removed = 0
        if info is not None:
            for work in info['works']:
                for tup in work['millnums']:
                    if millnum in tup:
                        work['millnums'].pop(work['millnums'].index(tup))
                        removed = removed + 1
        self.mongo.db.annotation.update({'_id' : info['_id']}, info)
        return removed


    def make_author(self,resp):
        """ Make an Author db record from a catalog record and insert it in the database

        :param resp: the response from teh catalog lookup
        :type resp: dict

        :return: the new Author db record
        :rtype: dict
        """
        author = {}
        author['name'] = resp['authority_name']
        author['cts_id'] = resp['canonical_id']
        author['works'] = []
        a_id = self.mongo.db.annotation.insert(author)
        new_auth = self.mongo.db.annotation.find_one({'_id' : a_id})
        return new_auth


    def make_work(self,work_id, millnum, pasg):
        """ Make a work record from a catalog record

        :param work_id: the CTS URN of a work
        :type work_id: string
        :param millnum: the Milliet number
        :type millnum: string
        :param pasg: the passage component from the work
        :type pasg: string

        :return: the work record
        :rtype: dict
        """
        w_resp = self.catalog.lookup_work(work_id)
        work = {}
        for w in w_resp:
            if w['urn_status'] is not 'invalid':
                work['title'] = w['title_eng']
                work['cts_id'] = w['work']
                l = [[millnum, pasg]]
                work['millnums'] = l
        return work

    def process_comm(self,comm_list):
        """ Extract a sorted list of milliet numbers from a set of commentary annotations

        :param comm_list: set of commentary annotations
        :type comm_list: list

        :return: sorted list of milliet numbers
        :rtype: list
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
