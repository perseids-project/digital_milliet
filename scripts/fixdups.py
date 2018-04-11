#!/usr/bin/env python
# Used to fix duplicate milliet/author mappings
from flask import Flask
from digital_milliet.digital_milliet import DigitalMilliet
from digital_milliet.lib.author_builder import AuthorBuilder

app = Flask('digital_milliet')
dm = DigitalMilliet(app, config_files=["config.cfg"])
person = {
    "@id": "http://data.perseus.org/sosol/users/Val%C3%A9rie%20Toillon",
    "type": 'Person',
    "name": "Valérie Toillon"
}
mongo = dm.get_db()
authors = dm.authors

millnums = {}
if __name__ == "__main__":
    with app.app_context():
        for author in authors.search(query="34", milliet_id=True):
            for work in author['works']:
                topop = []
                for idx, tup in enumerate(work['millnums']):
                    print(str(tup[0]) + ":" + str(tup[1]))
                    if tup[0] in millnums:
                        if tup[1] in millnums[tup[0]]:
                            topop.append(idx)
                        else:
                            millnums[tup[0]].append(tup[1])
                    else:
                        millnums[tup[0]] = [tup[1]]
                for index in sorted(topop, reverse=True):
                    del work['millnums'][index]
            authors.collection.update({'_id': author['_id']}, author)
