.. image:: https://travis-ci.org/perseids-project/digital_milliet.svg?branch=master
   :target: https://travis-ci.org/perseids-project/digital_milliet
.. image:: https://coveralls.io/repos/perseids-project/digital_milliet/badge.svg?branch=master
   :target: https://coveralls.io/r/perseids-project/digital_milliet?branch=master
.. image:: https://readthedocs.org/projects/pip/badge/?version=latest
   :target: http://digital-milliet.readthedocs.io/en/latest

Full Documentation at http://digital-milliet.readthedocs.io/en/latest/

Overview
========

The Digitat Milliet is a Python Flask Application backed by a Mongo DB database.  It supports the creation and display
of an interactive collection of ancient Greek and Latin texts about painting. It is a digital interpretation of
"The Recueil des textes grecs et latins relatifs à la peinture ancienne" (“Collection of Greek and Latin Texts
Concerning Ancient Painting”), the initiative of a French academic painter, Paul Milliet, who had a passion for ancient
Greek culture.

Installation Instructions
*************************

The following instructions are for setting up a Development environment for Digital Milliet.

Install Prerequisites:

* mongodb
* python 3.5, pip and virtualenv

.. code-block:: shell

    sudo apt-get install -y python3-pip python3-dev build-essential mongo

Clone the repository

.. code-block:: shell

    git clone https://github.com/perseids-project/digital_milliet

Setup the sample data

.. code-block:: shell

    mongorestore digital_milliet/db/sample

Create a virtual environment

.. code-block:: shell

    cd digital_milliet
    virtualenv -p /path/to/python3 venv
    source venv/bin/activate
    python setup.py install

Run the code, installing test fixtures and with a fixed user:

.. code-block:: shell

    python runtest.py --install --loggedin

Or deploy in Docker container

.. code-block:: shell

    git clone https://github.com/perseids-project/digital_milliet
    cd digital_milliet 
    docker build -t digital_milliet_image .
    docker run -p 5000:5000 -t -i digital_milliet_image

For production deployment, see Puppet manifests in the puppet subdirectory of this repository.

Design: Motivation, Standards, Dependencies
**************************************************
The aim behind the design of the application was to support the representation of each entry in the original "Recueil"
as a graph of annotations.

The primary annotation of a Digital Milliet graph/record set is a Commentary targeting
a stable CTS URN identifier of the primary source Greek or Latin text which was the subject of the entry in the "Receuil".
This commentary annotation gets assigned an identifier which includes the original number of the entry in the "Receui".
Throughout the code and interface, this is referred to as the "Milliet Number".

Additional annotations in each graph include a Bibliography, French and English translations of the primary source text,
as well as images representing the described artwork or related material and semantic tag annotations on the images,
the primry source texts, the translations and the commentary.

Entries are indexed for browsing both by Milliet Number and Author/Work/Passage of the target primary source text passage.

The Digital Milliet application retrieves Author and Work metadata for each primary source text is from the
Perseus Catalog (http://catalog.perseus.org/).

We have used a non-standard form of a CITE URN to assign identifiers to each individual annotation in the graph. This may 
eventually be replaced by UUIDs or other identifier system.

In order to facilitate data reuse and interoperability we represent these annotations according to the Open Annotation
data model, a standard data model for serializing annotations on resources in the world wide web.
(This model has now evolved into the W3C Web Annotation Model).

The original design called for primary source texts and translations to be identified only by their CTS URN identifiers
and all textual passages retrieved at runtime from CTS Repositories.

However, as many of the texts and/or translations we need to refer to are not yet available online at a published CTS
API endpoint, and the stability and long term sustainability of such end points are not clear, the application design
was changed to enabled textual content to be included in addition to or instead of the CTS URN identifier of a text or
translation.

The Digital Milliet application  depends upon components of the CapiTainS suite (https://github.com/capitains)
for its interaction with CTS endpoints and validation of CTS URN syntax.

The application uses the IIIF standard for image referencing and annotations and reuses the open source
Mirador Viewer (http://projectmirador.org/) to provide image display and annotation functionality.

A design for semantic tagging of textual content has not yet been decided upon.


Workflow
********

The primary workflow for entering a new entry in the Digital Milliet is described in the diagram below. 

.. image:: https://github.com/perseids-project/digital_milliet/blob/master/doc/digitalmillietnewcommentaryworkflow.png?raw=true

Individual components of an entry can also be edited or added separately after the initial data entry, via the Edit interface.  

Image annotations can be added, edited and deleted directly using the Mirador viewer. 

Authentication and Authorization
********************************
The Digital Milliet application itself does not provide a user model or any AAI functionality.

The Create, Update and Delete functionality of the Digital Milliet application can be protected by the OAuth2 protocol.
The location of the OAuth2 endpoint and other details must be supplied in these configuration settings:

.. code-block:: shell

    OAUTH_NAME = "digitalmilliet"
    OAUTH_CONSUMER_KEY = ''
    OAUTH_CONSUMER_SECRET =''
    OAUTH_REQUEST_TOKEN_PARAMS = {'scope': 'read'}
    OAUTH_BASE_URL = ''
    OAUTH_ACCESS_TOKEN_URL = ''
    OAUTH_ACCESS_TOKEN_METHOD = "POST"
    OAUTH_REQUEST_TOKEN_URL = None
    OAUTH_AUTHORIZE_URL = ''
    OAUTH_CALLBACK_URL = '<digmill_application_host>/oauth/authorized'


The deployment at https://digmill.perseids.org uses Perseids (https://sosol.perseids.org/sosol) as its OAuth2 provider.
Perseids in turn delegates to Social Identity providers for user authentication.  Perseids assigns a URI identifier to
authenticated users and users supply a public-facing full name that they wish to be affiliated with their Perseids account.
This information (the Perseids User URI and Full Name) are added as the creator associated with annotations created in
the Digital Milliet application. Once a record is created, if it's edited by a user other than the creator, that user is
added as an additional editor in the updated annotations.

Although not recommended for production use, it is possible to disable the OAuth2 protection by setting the name and URI
to associate with all records via the `OAUTH_USER_OVERRIDE` configuration setting.  This could be used in combination with a simpler authentication method such as HTTP Basic Authorization.

OAuth2 provides Authentication but not Authorization support. (By Authorization we mean restricting create/update/delete
access of Digital Milliet entries to only specific authenticated users.) Implementing a full user model and role-based
authorization was out of scope for development of the Digital Milliet application.  A potential future goal is to use
the Perseids platform to provide editorial review board functionality, removing the ability to edit annotations directly
in the Digital Milliet application.

With this goal in mind, we implemented a Perseids-specific stop-gap solution to provide Authorization functionality to
the Digital Milliet application.  The application configuration allows for the specification of the identifier of a
Perseids review community (via the `ENFORCE_COMMUNITY_ID` setting).  If this is specified, then authenticated users
must be a member of the Perseids Community with that id in order to be able to create, edit or delete entries in the
Digital Milliet. If the `ENFORCE_COMMUNITY_ID` setting is left empty, this functionality is disabled and all
authenticated users can create, edit or delete entries.

Configuration
*************
All deployment specific variables and dependencies are specified in an external configuration file. By default the application looks for a configuration file named `config.cfg` in the digital_milliet base directory.  An alternate
path can be supplied in an argument to the DigitalMilliet Flask Application:

.. code-block:: python

    DigitalMilliet(app, config_file="path/to/your/config.cfg")


The default contents of this configuration file, with explanation of each setting, is provided below:

.. code-block:: shell

      # Name of the Mongo database
      MONGO_DBNAME = 'app'

      # Secret key for Flask session
      SECRET_KEY = 'development is fun'

      # Perseids OAUTH Setup
      # OAUTH_CONSUMER_KEY and OAUTH_CONSUMER_SECRET must be supplied by Perseids Administrator for Production use
      OAUTH_NAME = "digitalmilliet"
      OAUTH_CONSUMER_KEY = 'dummy'
      OAUTH_CONSUMER_SECRET = 'dummy'
      OAUTH_REQUEST_TOKEN_PARAMS = {'scope': 'read'}
      OAUTH_BASE_URL = 'https://sosol.perseids.org/sosol/api/v1/'
      OAUTH_ACCESS_TOKEN_URL = 'https://sosol.perseids.org/sosol/oauth/token'
      OAUTH_ACCESS_TOKEN_METHOD = "POST"
      OAUTH_REQUEST_TOKEN_URL = None
      OAUTH_AUTHORIZE_URL = 'https://sosol.perseids.org/sosol/oauth/authorize'
      OAUTH_CALLBACK_URL = 'https://digmill.perseids.org/digmil/oauth/authorized'

      AUTHORS_COLLECTION = "annotation"

      # Set this to the ID for the Perseids community id in which membership enables Digital Milliet editorial permissions
      ENFORCE_COMMUNITY_ID = None

      # Not to be used in Production: eases development without OAuth Setup
      OAUTH_USER_OVERRIDE = { 'oauth_user_uri' : 'http://sampleuseruri', 'oauth_user_name': 'Sample User' }

      # Perseus Catalog API - Used for Lookup of Author and Work Metadata
      CATALOG_API_URL = 'http://catalog.perseus.org/cite-collections/api'
      CITE_URI_PREFIX = 'http://perseids.org/collections/'
      CITE_COLLECTION = 'urn:cite:perseus:digmil'

      # CTS API Endpoint for Retrieval of Primary Source Texts and Translations
      CTS_BROWSE_URL = 'https://cts.perseids.org'
      CTS_API_URL = 'https://cts.perseids.org/api/cts/'
      CTS_API_VERSION = 5
