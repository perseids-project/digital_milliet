import json

from digital_milliet.lib.oauth import OAuthHelper
from flask import render_template, request, jsonify, redirect, session, flash, url_for


class Views(object):

    def __init__(self, app=None, parser=None, db=None, builder=None):
        self.app = app
        self.parser = parser
        self.mongo = db
        self.builder = builder
        app.add_url_rule('/', view_func=self.index)
        app.add_url_rule('/index', view_func=self.index)
        app.add_url_rule('/about', view_func=self.about)
        app.add_url_rule('/search', view_func=self.search, methods=['POST'])
        app.add_url_rule('/commentary', view_func=self.commentary)
        app.add_url_rule('/commentary/<millnum>', view_func=self.millnum)
        app.add_url_rule('/edit/<millnum>', view_func=self.edit)
        app.add_url_rule('/edit/save_edit', view_func=self.save_edit, methods=['POST'])
        app.add_url_rule('/create', view_func=self.create, methods=['POST'])
        app.add_url_rule('/api/commentary/<millnum>', view_func=self.api_data_get, methods=['GET'])
        app.add_url_rule('/new', view_func=self.new,methods=['GET', 'POST'], strict_slashes=False)

    def index(self):
        return render_template('index.html')

    def about(self):
        return render_template('about.html')

    def search(self):
        form = request.form
        if form['dropdown'] == "Author":
            res = self.mongo.db.annotation.find({"name": form['value']})
        else:
            res = self.mongo.db.annotation.find({"works.title": form['value']})

        if res.count() == 0:
            res = None

        return render_template('search.html', res=res)

    def commentary(self):
        #add_to_existing_db()
        comm_list = self.mongo.db.annotation.find({"commentary": {'$exists' : 1}}).sort([("commentary.hasBody.@id" , 1)])
        auth_list = self.mongo.db.annotation.find({"cts_id": {'$exists' : 1}}).sort([("name" , 1)])
        millnum_list = self.parser.process_comm(comm_list)
        return render_template('commentary/list.html', millnum_list=millnum_list, auth_list=auth_list)

    def millnum(self, millnum):
        parsed_obj, auth_info = self.parser.get_it(millnum)
        if 'orig_uri' in parsed_obj:
            session['cts_uri'] = parsed_obj['orig_uri']

        return render_template('/commentary/commentary.html', obj=parsed_obj, info=auth_info, millnum=millnum)

    @OAuthHelper.oauth_required
    def edit(self, millnum):
        parsed_obj, auth_info = self.parser.get_it(millnum)

        return render_template('/commentary/edit.html', millnum=millnum, obj=parsed_obj)

    @OAuthHelper.oauth_required
    def save_edit(self):
        form = request.form
        saved = self.parser.edit_save(form)
        if saved:
            flash('Edit successfully saved','success')
        else:
            flash('Error!','danger')

        return redirect('commentary')

    #for catching requests from the perseids-client-apps form and saving the data
    @OAuthHelper.oauth_required
    def create(self):
        data = request.form.to_dict()
        if "iiif[]" in data:
            data["iiif"] = request.form.getlist("iiif[]")
            data["iiif_publisher"] = request.form.getlist("iiif_publisher[]")
        millnum = self.parser.save_from_form(data)
        if millnum is not None:
            flash('Annotation successfully created!','success')
            return redirect('commentary/' + str(millnum))
        else:
            flash('Error saving!','danger')
            return redirect('new')

    def api_data_get(self, millnum):
        res = self.mongo.db.annotation.find_one_or_404({"commentary.hasBody.@id": "http://perseids.org/collections/urn:cite:perseus:digmil."+millnum+".c1"})
        #have to remove the _id from mongo because it is bson and bson breaks the json
        del res['_id']
        return jsonify(res)

    @OAuthHelper.oauth_required
    def new(self):
        return render_template(
            'commentary/enter.html',
            cts_api=self.app.config['CTS_API_URL'],
            cts_browse = self.app.config['CTS_BROWSE_URL'],
            cts_version = self.app.config['CTS_API_VERSION']
        )

