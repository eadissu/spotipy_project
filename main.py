import requests
import urllib.parse
from datetime import datetime

from flask import Flask, redirect, request, jsonify, session


app = Flask(__name__)
app.secret_key = '53d355f8-571a-4590-a310-1f95579440851'

CLIENT_ID='8d7ad77d655b4509a54d8f842b409e2e'
CLIENT_SECRET='fe0c23212bfe46858fc51a15c1fa6606'
REDIRECT_URI='http://localhost:5000/callback'

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

@app.route('/')
def index():
  return "<p>Welcome to my Spotify App<p> <a href='/login'>Login with Spotify</a>" # redierect to login end point

# Login User
@app.route('/login')
def login():
  scope = 'user-read-private user-read-email'

  params = {
    'client_id': CLIENT_ID,
    'response_type': 'code',
    'scope': scope,
    'redirect_uri': REDIRECT_URI,
    'show_dialog': True # usually false -> for testing purposes
  }

  auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

  return redirect(auth_url)

# Call back enpoint
@app.route('/callback')
def callback():
  
  # login was unsuccessful
  if 'error' in request.args:
    return jsonify({"error": request.args['error']})
  
  # login was successful
  if 'code' in request.args:

    # build a request body to get access token
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

    return redirect('/playlists')
  

# retrieves current user's playlists
@app.route('/playlists')
def get_playlists():
  
  # error logging in
  if 'access_token' not in session:
    return redirect('/login')
  
  # check if token has expired
  if datetime.now().timestamp() > session['expires_at']:
    return redirect('/refresh-token')
  
  # we're good to go atp
  headers = {
    'Authorization': f"Bearer {session['access_token']}"
  }

  response = requests.get(API_BASE_URL + 'me/playlists', headers=headers)
  playlists = response.json()

  return jsonify(playlists)


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