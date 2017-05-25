Database Schema
###############

The Digital Milliet stores all data in MongoDB.

Digital Milliet commentary entries are stored in the `annotations` collection.

Author Records are stored in the collection named in the Digital Milliet config file setting `AUTHORS_COLLECTION`.

IIIF Image annotations are stored in the `mirador` collection.

(A future enhancement to externalize all collection names is requested in https://github.com/perseids-project/digital_milliet/issues/58)

The schema for the database objects is depicted here:

.. image:: https://github.com/perseids-project/digital_milliet/blob/master/doc/digitalmillietannotationsschema.png?raw=true

See also the test fixtures for examples of database entries.






