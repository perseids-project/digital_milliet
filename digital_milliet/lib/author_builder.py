#!/usr/bin/python

from flask import request, jsonify, url_for, session
import os, requests
import re
from MyCapytain.common.reference import URN
from bson.objectid import ObjectId


class AuthorBuilder(object):
    """ Provides methods for building new Author records in the database
    """

    def __init__(self, db=None, catalog=None, collection_name="annotation"):
        """ Constructor

        :param db: Mongo Db Handle
        :type db: PyMongo
        :param catalog: Catalog API Manager
        :type catalog: Catalog
        """
        self.mongo = db
        self.catalog = catalog
        self.__collection_name__ = collection_name

    @property
    def collection(self):
        """ Quick access to Mongo collection
        """
        return getattr(self.mongo.db, self.__collection_name__)

    def get_author(self, cts_id):
        """ Retrieve an author record by CTS ID

        :param cts_id: CTS Identifier
        :return: Author Record
        """
        return self.collection.find_one({"cts_id": cts_id})

    def get_author_by_mongoId(self, _id):
        """ Retrieve an author record by Mongo Id

        :param _id: Mongo Unique Identifier
        :return: Author Record
        """
        return self.collection.find_one({"_id": _id})

    def update_author(self, cts_id, author_record):
        """ Update author identified by CTS_ID

        :param cts_id: CTS Identifier
        :param author_record: Updated Author Record
        :return: Result of update
        """
        return self.collection.update({'cts_id': cts_id}, author_record)

    def author_db_build(self, data_dict):
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

            URN(target)
            millnum = cite_urn.split('.')[2]
            t_parts = target.split(':')
            urn_parts = t_parts[3].split('.')
            pasg = t_parts[4]
            auth_id = urn_parts[0]
            work_id = ':'.join(t_parts[0:3]) + ':' + '.'.join(urn_parts[0:2])

            author = self.get_author(auth_id)
            if author is None:
                response_dict = self.catalog.lookup_author(auth_id)
                for resp in response_dict:
                    if resp['urn_status'] is not 'invalid':
                        author = self.make_author(resp)

            # We may still not have an author here, if the catalog lookup didn't succeed
            if author is not None:
                works = author['works']
                if not works:
                    works.append(self.make_work(work_id, millnum, pasg))
                else:
                    work = next((ent for ent in works if 'cts_id' in ent and ent['cts_id'] == work_id), None)
                    if work is None:
                        works.append(self.make_work(work_id, millnum, pasg))
                    else:
                        exists = [duet for duet in work["millnums"] if duet == [millnum, pasg]]
                        if len(exists) == 0:
                            work['millnums'].append([millnum, pasg])

                self.update_author(author['cts_id'], author)
            else:
                print("Unable to get catalog info for " + target)
        except TypeError as err:
            print("Invalid data for author build", err)
            pass
        except KeyError as err:
            print("Invalid data for author build", err)
            pass
        except ValueError as err:
            print("Invalid data for author build", err)
            pass
        except:
            print("Invalid data for author build")
            pass

    def make_author(self, resp):
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
        a_id = self.collection.insert(author)
        new_auth = self.get_author_by_mongoId(a_id)
        return new_auth

    def make_work(self, work_id, millnum, pasg):
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

    def process_comm(self, comm_list):
        """ Extract a sorted list of milliet numbers from a set of commentary annotations

        :param comm_list: set of commentary annotations
        :type comm_list: list

        :return: sorted list of milliet numbers
        :rtype: list
        """
        millnum_list = []
        convert = lambda text: int(text) if text.isdigit() else text
        alphanum_key = lambda key: [convert(re.split('([A-Za-z]+)', key)[0])]
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
        return sorted(millnum_list, key=alphanum_key)
