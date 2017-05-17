from flask_oauthlib.client import OAuth
from flask import redirect, url_for, session, request, jsonify, render_template
from functools import wraps

class OAuthHelper(object):
    """ Helper class providing OAuth2 functionality to the application
    Implements flask_oauthlib.client
    """

    def __init__(self,app):
        """ Constructor

        :param app: the wrapped flask app
        :type app: Flask
        """
        oauth = OAuth(app)
        self.authobj = oauth.remote_app(
            app.config['OAUTH_NAME'],
            consumer_key=app.config['OAUTH_CONSUMER_KEY'],
            consumer_secret=app.config['OAUTH_CONSUMER_SECRET'],
            request_token_params=app.config['OAUTH_REQUEST_TOKEN_PARAMS'],
            base_url=app.config['OAUTH_BASE_URL'],
            request_token_url=app.config['OAUTH_REQUEST_TOKEN_URL'],
            access_token_method=app.config['OAUTH_ACCESS_TOKEN_METHOD'],
            access_token_url=app.config['OAUTH_ACCESS_TOKEN_URL'],
            authorize_url=app.config['OAUTH_AUTHORIZE_URL']
        )
        self.authobj.tokengetter(self.oauth_token)
        self.authcallback = app.config['OAUTH_CALLBACK_URL']
        self.enforce_community_id = app.config['ENFORCE_COMMUNITY_ID']
        self.auth_override = None
        if 'OAUTH_USER_OVERRIDE' in app.config:
            self.auth_override = app.config['OAUTH_USER_OVERRIDE']
        app.add_url_rule('/oauth/login',view_func = self.r_oauth_login)
        app.add_url_rule('/oauth/authorized',view_func = self.r_oauth_authorized)
        app.add_url_rule('/oauth/logout',view_func = self.r_oauth_logout)

    def r_oauth_login(self):
        """ Route for OAuth2 Login

        :param next: next url
        :type next: string

        :return: Redirects to OAuth Provider Login URL
        """
        session['next'] = request.args.get('next', '')
        # overrides the oauth functionality for ease of development
        # this override should not be used in production
        if self.auth_override is not None:
            session['oauth_user_uri'] = self.auth_override['oauth_user_uri']
            session['oauth_user_name'] = self.auth_override['oauth_user_name']
            return redirect(session['next'])

        callback_url = self.authcallback
        if callback_url is None:
            callback_url = url_for('.r_oauth_authorized', _external=True)
        return self.authobj.authorize(callback=callback_url)

    def r_oauth_authorized(self):
        """ Route for OAuth2 Authorization callback

        :return: renders template
        """
        resp = self.authobj.authorized_response()
        if resp is None:
            return 'Access denied: reason=%s error=%s' % (
                request.args['error'],
                request.args['error_description']
            )
        session['oauth_token'] = (resp['access_token'], '')
        user = self.authobj.get('user')
        ## TODO this is too specific to Perseids' api model. We should externalize.
        if not self.user_in_community(user.data['user']['communities']):
            return 'Access denied: reason=%s error=%s' % (
                "Not in Community",
                "Not in Community"
            )
        session['oauth_user_uri'] = user.data['user']['uri']
        session['oauth_user_name'] = user.data['user']['full_name']
        if 'next' in session and session['next'] is not None and session['next'] != '':
            return redirect(session['next'])
        else:
            return render_template('authorized.html', username=session['oauth_user_name'])

    def r_oauth_logout(self):
        """ Route to clear the oauth data from the session

        :param next: next url
        :type next: string

        :return: redirects to next or renders template
        """
        session.pop('oauth_user_uri', None)
        session.pop('oauth_user_name', None)
        next = request.args.get('next','')
        if next is not None and next != '':
            return redirect(next)
        else:
            return render_template('index.html')

    def oauth_token(self,token=None):
        """ tokengetter function

        :param token: the Oauth token
        :type token: string

        :return: the current access token
        :rtype: string
        """
        return session.get('oauth_token')

    def current_user(self):
        """ Gets the current user from the session

        :return: { uri => <uri>, name => <name> }
        :rtype: dict
        """
        if session and session['oauth_user_uri']:
            user = {'uri': session['oauth_user_uri']}
            if 'oauth_user_name' in session:
                user['name'] = session['oauth_user_name']
            else:
                user['name'] = session['oauth_user_uri']
            return user
        else:
            return None

    def user_in_community(self, user_communities=[]):
        """ Checks to see if the user is the authorized community for editing

        This is a hack specific to the Perseids OAuth provider used as a way
        to limit editing of DM records to members of a specific community in Perseids
        Eventually editing could be delegated entirely to Perseids

        :return: True if the user name is listed in the configured community members,
                 False if the user name is not listed
        :rtype: bool
        """
        if self.enforce_community_id:
            return user_communities.__contains__(self.enforce_community_id)
        else:
            return True

    def oauth_required(f):
        """ decorator to add to a view to require an oauth user

        :return: decorated function
        :rtype: func
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'oauth_user_uri' not in session or session['oauth_user_uri'] is None:
                if request.method == 'POST':
                    # we should really handle redirects on POSTS too but they should only happen if the session
                    # timed out in between requesting a page and submitting it so to keep it simple just redirect
                    # POSTs to the index page
                    next = url_for('.index',_external=True)
                else:
                    next = request.url
                return redirect(url_for('.r_oauth_login', next=next, _external=True))
            return f(*args,**kwargs)
        return decorated_function
