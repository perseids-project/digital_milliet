from digital_milliet.lib.oauth import OAuthHelper
from flask import render_template, request, redirect, session, flash


class Views(object):
    def __init__(self, app=None, commentaries=None, db=None, authors=None, mirador=None):
        """ Main view system

        :param app: Flask APP
        :type app: Flask
        :param commentaries: Commentary Component
        :type commentaries: CommentaryHandler
        :param db: Mongo Data Resolver
        :type db: PyMongo
        :param authors: Author Component
        :type authors: AuthorBuilder
        :param mirador: Mirador Component
        :type mirador: Mirador
        """
        self.app = app
        self.commentaries = commentaries
        self.mongo = db
        self.authors = authors
        self.mirador = mirador
        app.add_url_rule('/', view_func=self.index)
        app.add_url_rule('/index', view_func=self.index)
        app.add_url_rule('/about', view_func=self.about)
        app.add_url_rule('/search', view_func=self.search, methods=['GET'])
        app.add_url_rule('/commentary', view_func=self.commentary)
        app.add_url_rule('/commentary/<millnum>', view_func=self.millnum)
        app.add_url_rule('/edit/<millnum>', view_func=self.edit)
        app.add_url_rule('/edit/save_edit', view_func=self.save_edit, methods=['POST'])
        app.add_url_rule('/delete', view_func=self.delete, methods=['POST'])
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
                res = self.authors.search(query=query, name=True)
            else:
                res = self.authors.search(query=query, works=True)
            if res.count() == 0:
                res = None

        return render_template('search.html', res=res)

    def commentary(self):
        """ List available commentaries and Milliet entries
        """
        millnum_list = self.commentaries.get_milliet_identifier_list()
        auth_list = self.authors.author_list()
        return render_template('commentary/list.html', millnum_list=millnum_list, auth_list=auth_list)

    def millnum(self, millnum):
        """ Read a Milliet entry
        """
        parsed_obj, auth_info = self.commentaries.get_milliet(millnum)
        if 'orig_uri' in parsed_obj:
            session['cts_uri'] = parsed_obj['orig_uri']

        return render_template('commentary/commentary.html', obj=parsed_obj, info=auth_info, millnum=millnum)

    @OAuthHelper.oauth_required
    def delete(self):
        millnum = request.form['millnum']
        removed = self.commentaries.remove_milliet(millnum)
        if removed > 0:
          flash('Record for ' + millnum + ' removed.','success')
        else:
          flash('Error removing record for ' + millnum + '.','danger')
        return redirect('commentary')

    @OAuthHelper.oauth_required
    def edit(self, millnum):
        """ Edit the Milliet identified by millnum
        """
        parsed_obj, auth_info = self.commentaries.get_milliet(millnum)

        return render_template('commentary/edit.html', millnum=millnum, obj=parsed_obj)

    @OAuthHelper.oauth_required
    def save_edit(self):
        """ Save the edit form
        """
        form = request.form.to_dict()
        if "iiif[]" in form:
            form["iiif"] = request.form.getlist("iiif[]")
            form["iiif_publisher"] = request.form.getlist("iiif_publisher[]")
        saved = self.commentaries.update_commentary(form)
        if saved:
            flash('Edit successfully saved', 'success')
        else:
            flash('Error!', 'danger')

        return redirect('commentary')

    @OAuthHelper.oauth_required
    def create(self):
        """ Create a new entry
        """
        data = request.form.to_dict()
        if "iiif[]" in data:
            data["iiif"] = request.form.getlist("iiif[]")
            data["iiif_publisher"] = request.form.getlist("iiif_publisher[]")
        millnum = self.commentaries.create_commentary(data)
        if millnum is not None:
            flash('Annotation successfully created!','success')
            return redirect('commentary/' + str(millnum))
        else:
            flash('Error saving!','danger')
            return redirect('new')

    def api_data_get(self, millnum):
        """ Read a Milliet entry as a JSON Bag
        """
        res = self.commentaries.get_milliet(milliet_id=millnum, simplify=False)
        res["iiif_annotations"] = self.mirador.from_collection(millnum)
        return self.mirador.dump(res)

    @OAuthHelper.oauth_required
    def new(self):
        return render_template(
            'commentary/enter.html',
            cts_api=self.app.config['CTS_API_URL'],
            cts_browse=self.app.config['CTS_BROWSE_URL'],
            cts_version=self.app.config['CTS_API_VERSION']
        )

