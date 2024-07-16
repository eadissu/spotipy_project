# Source = https://www.youtube.com/watch?v=olY_2MW4Eik&list=LL&index=4

import urllib.parse
import requests
import uuid
import base64

from datetime import datetime
from flask import Flask, redirect, request, jsonify, session, render_template, url_for


app = Flask(__name__)
app.secret_key = str(uuid.uuid4())

CLIENT_ID='8d7ad77d655b4509a54d8f842b409e2e'
CLIENT_SECRET='fe0c23212bfe46858fc51a15c1fa6606'
REDIRECT_URI='http://localhost:5000/callback'

AUTH_URL = 'https://accounts.spotify.com/authorize?'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

@app.route('/')
def home():
    return redirect(url_for('index'))


@app.route('/index')
def index():
    return render_template('index.html')  # Assuming you have an 'index.html' template

# For Auto Deployment !
@app.route("/update_server", methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('/home/eadissu/spotipy_project')
        origin = repo.remotes.origin
        origin.pull()
        return 'Updated PythonAnywhere successfully', 200
    else:
        return 'Wrong event type', 400

# Login User
@app.route('/login')
def login():
  scope = 'user-read-private'

  params = {
    'client_id': CLIENT_ID,
    'response_type': 'code',
    'scope': scope,
    'redirect_uri': REDIRECT_URI,
    'show_dialog': True, # usually False -> for testing purposes use True
    'state': app.secret_key
  }

  auth_url = f"{AUTH_URL}{urllib.parse.urlencode(params)}"

  return redirect(auth_url)

# Call back enpoint
@app.route('/callback')
def callback():
  
  # login was unsuccessful
  if 'error' in request.args:
    return jsonify({"error": request.args['error']})
  
  
  # login was successful
  if 'code' in request.args:

    code = request.args.get('code')
    if 'state' in request.args:

      # build a request body to get access token
      auth_options = {
        'url': TOKEN_URL, 
        'data': {
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code'
        },
        'headers': {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        }
      }
       
      '''
      
      req_body = {
        'code': request.args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET

      }
      

      response = requests.post(TOKEN_URL, data=req_body)
      token_info = response.json()

      session['access_token'] = token_info['access_token']
      session['refresh_token'] = token_info['refresh_token']
      session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']

      return redirect('/index')
    '''
      
      session = requests.post(auth_options['url'], data=auth_options['data'], headers=auth_options['headers'])
  
      if session.status_code == 200:
        print(jsonify(session.json()))
        return redirect('/index')
      else:
        return jsonify({'error': 'Failed to get access token'}), session.status_code
      
      


# retrieves current user's playlists
@app.route('/tracks')
def tracks():

  # get json of playlists
  output = get_playlists()

  # convert into tables!

  return render_template("tracks.html", tracks = output)

def get_playlists():

  access_token = session.get('access_token')

  # error logging in
  #if 'access_token' not in session:
  #  return redirect('/login')
  if not access_token:
        return jsonify({'error': 'Access token is required'}), 400
    
  
  # check if token has expired
  #if datetime.now().timestamp() > session['expires_at']:
  #  return redirect('/refresh-token')
  
  # we're good to go atp
  headers = {
    'Authorization': 'Bearer ' + access_token
  }



  response = requests.get(API_BASE_URL + 'me/playlists', headers=headers)

  toreturn = ""
  if response.status_code == 200:
    toreturn += "SUCCESS!!!\n"
    toreturn += str(response.json())
  else:
    toreturn += ("FAILED ??\n")
    toreturn += response.status_code 

  return toreturn



@app.route('/refresh-token')
def refresh_token():
  
  # no token
  if 'refresh_token' not in session:
    return redirect('/login')
  
  # token has expired
  if datetime.now().timestamp() > session['expires_at']:

    req_body = {
      'grant_type': 'refresh_token',
      'refresh_token': session['refresh_token'],
      'client_id': CLIENT_ID,
      'client_secret': CLIENT_SECRET
    }  

    response = requests.post(TOKEN_URL, data=req_body)
    new_token_info = response.jason()

    session['access_token'] = new_token_info['access_token']
    session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

    return redirect('/plalists')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
