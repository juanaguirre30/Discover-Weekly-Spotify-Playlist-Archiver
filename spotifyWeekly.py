# import necessary modules
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect

# initialize Flask app
app = Flask(__name__)

# set the name of the session cookie
app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'

# set a random secret key to sign the cookie
app.secret_key = 'SECRET'

# set the key for the token info in the session dictionary
TOKEN_INFO = 'token_info'

# Home Route 
@app.route('/')
def login():
    auth_url = create_spotify_oauth().get_authorize_url() # gets value of url given to user
    return redirect(auth_url) # redirecting to url

# Redirect Route
@app.route('/redirect')
def redirect_page():
    session.clear()
   
    code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('save_discover_weekly',_external=True))

# Save Discover Weekly Route 
@app.route('/saveDiscoverWeekly')
def save_discover_weekly():
    try: 
        token_info = get_token()
    except:
        print('User not logged in')
        return redirect("/")

    sp = spotipy.Spotify(auth=token_info['access_token']) # variable for all the API requests 

    current_playlists =  sp.current_user_playlists()['items']
    discover_weekly_playlist_id = None
    saved_weekly_playlist_id = None

    for playlist in current_playlists:
        if(playlist['name'] == 'Discover Weekly'):
            discover_weekly_playlist_id = playlist['id']
        if(playlist['name'] == 'Saved Weekly'):
            saved_weekly_playlist_id = playlist['id']
    
    if not discover_weekly_playlist_id:
        return 'Discover Weekly not found.'
    
    # creates spotify saved playlist if not already created 
    if not saved_weekly_playlist_id:
        temp_playlist = sp.user_playlist_create("juanaguirre158", 'Saved Weekly', True)
        saved_weekly_playlist_id = temp_playlist
    
    discover_weekly_playlist = sp.playlist_items(discover_weekly_playlist_id) # gets the discover weekly tracks 
    
    # loop through every song in discover weekly and append them into a list
    song_uris = []
    for song in discover_weekly_playlist['items']:
        song_uri= song['track']['uri']
        song_uris.append(song_uri)
    
    sp.user_playlist_add_tracks("juanaguirre158", saved_weekly_playlist_id, song_uris, None)

    return ('Discover Weekly songs added successfully')

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        redirect(url_for('login', _external=False))
    
    now = int(time.time())

    is_expired = token_info['expires_at'] - now < 60
    if(is_expired):
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])

    return token_info

# Allows for access of user's spotify
def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = '966f6896d45c4449bdd3f275249f5615',
        client_secret = 'SECRET',
        redirect_uri = url_for('redirect_page', _external=True),
        scope='user-library-read playlist-modify-public playlist-modify-private'
    )

app.run(debug=True)
