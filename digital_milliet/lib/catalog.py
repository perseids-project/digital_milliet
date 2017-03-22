#coding utf-8
import os, requests

class Catalog(object):
    """ Provides an interface to a Catalog API Endpoint
    which can lookup author and work records by CTS URN
    """

    def __init__(self,app=None):
        """ Constructor

        :param app:  The Flask App
        :type app: Flask
        """
        self.app = app
        self.api_endpoint = app.config['CATALOG_API_URL']

    def lookup_author(self, urn=None):
        """ Looks up an Author by authority id in the remote Catalog API endpoint

        :param urn: The authority id (i.e textgroup CTS URN)
        :type urn: string

        :return: response from the API (this should be abstracted)
        :rtype: dict
        """
        url = str(self.api_endpoint + '/authors/search?canonical_id=' + urn + '&format=json')
        return requests.get(url).json()

    def lookup_work(self,urn=None):
        """ Looks up an Work by authority id in the remote Catalog API endpoint

        :param urn: The authority id (i.e work CTS URN)
        :type urn: string

        :return: response from the API (we should abstract this)
        :rtype: dict
        """
        url = str(self.api_endpoint + '/works/search?work=' + urn + "&format=json")
        return requests.get(url).json()


