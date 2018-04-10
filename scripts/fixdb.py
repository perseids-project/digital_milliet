#!/usr/bin/env python
# Used to fix creator and contributor id in existing records
from flask import Flask
from digital_milliet.digital_milliet import DigitalMilliet
from digital_milliet.lib.commentaries import CommentaryHandler

app = Flask('digital_milliet')
dm = DigitalMilliet(app, config_files=["config.cfg"])
person = {
    "@id": "http://data.perseus.org/sosol/users/Val%C3%A9rie%20Toillon",
    "type": 'Person',
    "name": "Valérie Toillon"
}
mongo = dm.get_db()
commentaries = dm.commentaries

if __name__ == "__main__":
    with app.app_context():
        for obj in mongo.db.annotation.find({"commentary": {'$exists': 1}}):
            for type in ['commentary', 'bibliography', 'translation']:
                for i, item in enumerate(obj[type]):
                    contributors = obj[type][i].setdefault('contributor', [])
                    creator = obj[type][i].setdefault('creator', person)
                    id = obj[type][i]['creator'].pop('id', None)
                    if id is not None:
                        obj[type][i]['creator']['@id'] = id
                    new_contribs = []
                    for c in contributors:
                        id = c.pop('id', None)
                        if id != creator['@id']:
                            c['@id'] = id
                            new_contribs.append(c)
                    obj[type][i]['contributor'] = new_contribs

            mongo.db.annotation.save(obj)
