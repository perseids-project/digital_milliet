import json

from digital_milliet.lib.oauth import OAuthHelper
from flask import render_template, request, jsonify, redirect, session, flash, url_for


class Views(object):

    def __init__(self, app=None, parser=None, db=None, builder=None, mirador=None):
        self.app = app
        self.parser = parser
        self.mongo = db
        self.builder = builder
        self.mirador = mirador
        app.add_url_rule('/', view_func=self.index)
        app.add_url_rule('/index', view_func=self.index)
        app.add_url_rule('/about', view_func=self.about)
        app.add_url_rule('/search', view_func=self.search, methods=['GET'])
        app.add_url_rule('/commentary', view_func=self.commentary)
        app.add_url_rule('/commentary/<millnum>', view_func=self.millnum)
        app.add_url_rule('/edit/<millnum>', view_func=self.edit)
        app.add_url_rule('/edit/save_edit', view_func=self.save_edit, methods=['POST'])
        app.add_url_rule('/create', view_func=self.create, methods=['POST'])
        app.add_url_rule('/api/commentary/<millnum>', view_func=self.api_data_get, methods=['GET'])
        app.add_url_rule('/new', view_func=self.new, methods=['GET', 'POST'], strict_slashes=False)

    def index(self):
        return render_template('index.html')

    def about(self):
        return render_template('about.html')

    def search(self):
        """ Search results
        """
        query = request.args.get("query")
        res = None
        if query:
            if request.args.get("in") == "Author":
                res = self.mongo.db.annotation.find({"name": query})
            else:
                res = self.mongo.db.annotation.find({"works.title": query})

            if res.count() == 0:
                res = None

        return render_template('search.html', res=res)

    def commentary(self):
        """ List available commentaries and Milliet entries
        """
        comm_list = self.mongo.db.annotation.find({"commentary": {'$exists': 1}}).sort([("commentary.hasBody.@id", 1)])
        auth_list = self.mongo.db.annotation.find({"cts_id": {'$exists': 1}}).sort([("name", 1)])
        millnum_list = self.parser.retrieve_millietId_in_commentaries(comm_list)
        return render_template('commentary/list.html', millnum_list=millnum_list, auth_list=auth_list)

    def millnum(self, millnum):
        """ Read a Milliet entry
        """
        parsed_obj, auth_info = self.parser.get_milliet(millnum)
        if 'orig_uri' in parsed_obj:
            session['cts_uri'] = parsed_obj['orig_uri']

        return render_template('commentary/commentary.html', obj=parsed_obj, info=auth_info, millnum=millnum)

    @OAuthHelper.oauth_required
    def edit(self, millnum):
        """ Edit the Milliet identified by millnum
        """
        parsed_obj, auth_info = self.parser.get_milliet(millnum)

        return render_template('commentary/edit.html', millnum=millnum, obj=parsed_obj)

    @OAuthHelper.oauth_required
    def save_edit(self):
        """ Save the edit form
        """
        form = request.form.to_dict()
        if "iiif[]" in form:
            form["iiif"] = request.form.getlist("iiif[]")
            form["iiif_publisher"] = request.form.getlist("iiif_publisher[]")
        saved = self.parser.update_commentary(form)
        if saved:
            flash('Edit successfully saved','success')
        else:
            flash('Error!','danger')

        return redirect('commentary')

    @OAuthHelper.oauth_required
    def create(self):
        """ Create a new entry
        """

        data = request.form.to_dict()
        if "iiif[]" in data:
            data["iiif"] = request.form.getlist("iiif[]")
            data["iiif_publisher"] = request.form.getlist("iiif_publisher[]")
        millnum = self.parser.create_commentary(data)
        if millnum is not None:
            flash('Annotation successfully created!','success')
            return redirect('commentary/' + str(millnum))
        else:
            flash('Error saving!','danger')
            return redirect('new')

    def api_data_get(self, millnum):
        """ Read a Milliet entry as a JSON Bag
        """
        res = self.mongo.db.annotation.find_one_or_404(
            {"commentary.hasBody.@id": "http://perseids.org/collections/urn:cite:perseus:digmil."+millnum+".c1"}
        )
        del res['_id']
        res["annotations"] = self.mirador.from_collection(millnum)
        return self.mirador.dump(res)

    @OAuthHelper.oauth_required
    def new(self):
        return render_template(
            'commentary/enter.html',
            cts_api=self.app.config['CTS_API_URL'],
            cts_browse=self.app.config['CTS_BROWSE_URL'],
            cts_version=self.app.config['CTS_API_VERSION']
        )

