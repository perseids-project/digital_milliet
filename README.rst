.. image:: https://travis-ci.org/perseids-project/digital_milliet.svg?branch=master
   :target: https://travis-ci.org/perseids-project/digital_milliet
.. image:: https://coveralls.io/repos/perseids-project/digital_milliet/badge.svg?branch=master
   :target: https://coveralls.io/r/perseids-project/digital_milliet?branch=master
.. image:: https://readthedocs.org/projects/pip/badge/?version=latest
   :target: http://digital-milliet.readthedocs.io/en/latest

Digital Milliet
===============

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

Run the code

.. code-block:: shell

    python run.py


Or deploy in Docker container

.. code-block:: shell

    git clone https://github.com/perseids-project/digital_milliet
    docker build digital_milliet_image
    docker run -p 5000:5000 -t -i digital_milliet_image

For production deployment, see Puppetfile 



Design Overview
****************
The aim behind the design of the application was to support the representation of each entry in the original "Recueil"
as a graph of annotations, with the primary annotation being a Commentary targeting a stable CTS URN identifier
of the primary source Greek or Latin text which was the subject of the entry in the "Receuil". This commentary annotation
gets assigned an identifier which includes the original number of the entry in the "Receui". (Throughout the code and
interface, this is referred to as the "Milliet Number".) Additional annotations in each graph include a Bibliography,
French and English translations of the primary source text, and eventually Images representing the described artwork
and semantic tag annotations on the images, the primary source texts, the translations and the commentary.  Entries
are indexed for browsing both by Milliet Number and Author/Work/Passage of the target primary source text passage.
Author and Work information for each primary source text is retrieved from the Perseus Catalog (http://catalog.perseus.org/). 
We have used a non-standard form of a CITE URN to assign identifiers to each individual annotation in the graph. This may 
eventually be replaced by UUIDs or other identifier system.

In order to facilitate data reuse and interoperability we represent these annotations according to the Open Annotation
data model, a standard data model for serializing annotations on resources in the world wide web.
(This model has now evolved into the W3C Web Annotation Model). The original design called for primary source texts
and translations to be identified by their CTS URN identifiers and passages retrieved at runtime from CTS Repositories
but as many of the texts and/or translations we need to refer to are not yet available online at a published CTS
API endpoint, we also allow for embedded textual content instead of and in addition to the CTS URN identifiers.

Images, when implemented, will use the IIIF standard for referencing and annotation.  A design for semantic tagging
of textual content has not yet been decided upon.

The code depends upon components of the CapiTainS suite (https://github.com/capitains) for interaction with CTS endpoints and validation of CTS URN
syntax.

