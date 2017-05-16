#!/usr/bin/python

from flask import jsonify
from flask_pymongo import PyMongo
from digital_milliet.lib.oauth import OAuthHelper


class Mirador(object):
    """ Parses data for retrieval/storage to/from the database
    """
    def __init__(self, db, app):
        """ Parser object

        :param db: Mongo Db Handle
        :type db: PyMongo
        :param app: Flask App
        :type app: Flask
        """
        self.mongo = db
        self.app = app

        self.app.add_url_rule(
            '/api/mirador', view_func=self.search, methods=["GET"], endpoint="mirador_search")
        self.app.add_url_rule(
            '/api/mirador', view_func=self.create, methods=["PUT"], endpoint="mirador_create")
        self.app.add_url_rule(
            '/api/mirador/<annotationId>', view_func=self.update, methods=["POST"], endpoint="mirador_update")
        self.app.add_url_rule(
            '/api/mirador/<annotationId>', view_func=self.delete, methods=['DELETE'], endpoint="mirador_delete")

    def search(self):
        return None

    @OAuthHelper.oauth_required
    def create(self, commentary=None):
        return None

    @OAuthHelper.oauth_required
    def update(self, annotationId):
        return None

    @OAuthHelper.oauth_required
    def delete(self, annotationId):
        return None
