#!/usr/bin/python
from uuid import uuid4
from flask import Response, request
from flask_pymongo import PyMongo
from datetime import datetime
from digital_milliet.lib.oauth import OAuthHelper
from bson.json_util import dumps


class Mirador(object):
    """ Parses data for retrieval/storage to/from the database
    """
    def __init__(self, db, app, parser):
        """ Parser object

        :param db: Mongo Db Handle
        :type db: PyMongo
        :param app: Flask App
        :type app: Flask
        :param parser: Parser
        :type parser: Parser
        """
        self.mongo = db
        self.app = app
        self.parser = parser

        self.app.add_url_rule(
            '/api/mirador', view_func=self.search, methods=["GET"], endpoint="mirador_search")
        self.app.add_url_rule(
            '/api/mirador', view_func=self.create, methods=["PUT"], endpoint="mirador_create")
        self.app.add_url_rule(
            '/api/mirador/<annotationId>', view_func=self.update, methods=["POST"], endpoint="mirador_update")
        self.app.add_url_rule(
            '/api/mirador/<annotationId>', view_func=self.delete, methods=['DELETE'], endpoint="mirador_delete")

    @staticmethod
    def dump(content, code=200):
        return Response(
            dumps(content),
            mimetype='application/json',
            status=code
        )

    def get(self, image_uri=None, anno_id=None, _id=None, single=False):
        """ Retrieve annotations

        :param image_uri:
        :return:
        """
        if single is True:
            fn = self.mongo.db.mirador.find_one_or_404
        else:
            fn = self.mongo.db.mirador.find

        kwargs = {}
        if image_uri is not None:
            kwargs["on.full"] = image_uri
        if anno_id is not None:
            kwargs["@id"] = anno_id
        if _id is not None:
            kwargs["_id"] = _id

        return fn(kwargs)

    @staticmethod
    def simpleFormat(oAnnotation):
        del oAnnotation["_id"]
        oAnnotation["resource"] = [res for res in oAnnotation["resource"] if res["@type"] != "dctypes:Collection"]
        return oAnnotation

    def search(self):
        if request.args.get("noCollection") is not None:
            return self.dump([
                    self.simpleFormat(oAnnotation) for oAnnotation in self.get(image_uri=request.args.get("uri"))
                 ])
        else:
            return self.dump([
                {k: v for k, v in oAnnotation.items() if v not in ["_id"]}
                for oAnnotation in self.get(image_uri=request.args.get("uri"))
            ])

    @OAuthHelper.oauth_required
    def create(self):
        data = request.get_json()
        milliet_number = request.args.get("milliet_number")
        data["annotatedAt"] = datetime.now().isoformat()
        data["serializedAt"] = data["annotatedAt"]
        data["annotatedBy"] = self.parser.make_person()
        data["permissions"] = {
            "read": [],
            "update": [data["annotatedBy"]["@id"]],
            "delete": [data["annotatedBy"]["@id"]],
            "admin": [data["annotatedBy"]["@id"]]
        }
        data["@id"] = self.parser.make_uri(milliet_number, "anno-{}".format(uuid4()))

        if milliet_number is not None:
            data["resource"].append({
                "@type": "dctypes:Collection",
                "@id": self.parser.make_uri(milliet_number)
            })
        m_obj = self.mongo.db.mirador.insert(data)
        return self.dump(self.simpleFormat(self.get(_id=m_obj, single=True)), code=200)

    @OAuthHelper.oauth_required
    def update(self, annotationId):
        anno = {}
        return self.dump({}, code=200)

    @OAuthHelper.oauth_required
    def delete(self, annotationId):
        return None
