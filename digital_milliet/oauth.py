from flask_oauthlib.client import OAuth
from flask import redirect, url_for, session, request, jsonify


def __init__(self,app,oauth_name=None,oauth_key=None,oauth_secret=None,oauth_scope=None,oauth_access_token_url=None,
  oauth = OAuth(app)
  self.authobj = oauth.remote_app(
    oauth_name,
    consumer_key=oauth_key,
    consumer_secret=oauth_secret,
    request_token_params={'scope':oauth_scope},
    base_url=oauth_base_api_url,
    request_token_url=oauth_request_token_url,
    access_token_method='POST',
    access_token_url=oauth_access_token_url,
    authorize_url=oauth_authorize_url
  )
  self.authobj.tokengetter(self.oauth_token)
  self.authcallback = oauth_callback_url \

@app.route('/oauth/login')
def r_oauth_login(self):
  """
  Route for OAuth2 Login

  :param next next url
  :type str

  :return: Redirects to OAuth Provider Login URL
  """
  session['next'] = request.args.get('next','')
  callback_url = self.authcallback
  if callback_url is None:
    callback_url = url_for('.r_oauth_authorized', _external=True)
  return self.authobj.authorize(callback=callback_url)


@app.route('/oauth/authorized')
def r_oauth_authorized(self):
  """
  Route for OAuth2 Authorization callback
  :return: {"template"}
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
  session['oauth_user_uri'] = user.data['user']['uri']
  session['oauth_user_name'] = user.data['user']['full_name']
  if 'next' in session and session['next'] is not None:
    return redirect(session['next'])
  else:
    return render_template('authorized.html', username=session['oauth_user_name'])

@app.route('/oauth/logout')
def r_oauth_logout(self):
  """
  Route to clear the oauth data from the session
  :return: {"template"}
  """
  session.pop('oauth_user_uri', None)
  session.pop('oauth_user_name', None)
  next = request.args.get('next','')
  if next is not None:
    return redirect(session['next'])
  else:
    return render_template('index.html')

def oauth_token(token=None):
  """
  tokengetter function
  :return: the current access token
  :rtype str
  """
  return session.get('oauth_token')

@property
def current_user(self):
  """
  Gets the current user from the session
  :return { uri => <uri>, name => <name> }
  """
  if session['oauth_user_uri']:
    return { 'uri': session['oauth_user_uri'],
             'name': session['oauth_user_name'] or session['oauth_user_uri']}
  else:
    return None


def oauth_required(f):
  """
  decorator to add to a view to require an oauth user
  :return: decorated function
  """
  @wraps(f)
  def decorated_function(*args, **kwargs):
    if 'oauth_user_uri' not in session or session['oauth_user_uri'] is None:
      return redirect(url_for('.r_oauth_login', next=request.url))
    return f(*args,**kwargs)
  return decorated_function
