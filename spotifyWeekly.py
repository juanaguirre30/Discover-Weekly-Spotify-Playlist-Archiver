# Required modules importation
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect

# Flask application initialization
app = Flask(__name__)

# Configuring the session cookie name
app.config['SESSION_COOKIE_NAME'] = 'SpotifySession'

# Assigning a secret key for the session
app.secret_key = 'xyxyxyxyxyxyxyxyxy'

# Session key for storing token information
TOKEN_KEY = 'token_details'

# Route for user login
@app.route('/')
def login():
    oauth = setup_spotify_oauth()
    auth_url = oauth.get_authorize_url()
    return redirect(auth_url)

# Route to handle Spotify's redirect after authorization
@app.route('/callback')
def callback():
    session.clear()
    auth_code = request.args.get('code')
    token_data = setup_spotify_oauth().get_access_token(auth_code)
    session[TOKEN_KEY] = token_data
    return redirect(url_for('store_discover_weekly', _external=True))

# Route to store Discover Weekly tracks in a playlist
@app.route('/storeDiscoverWeekly')
def store_discover_weekly():
    try:
        token_data = retrieve_token()
    except Exception as error:
        print(f'Token retrieval error: {error}')
        return redirect("/")

    sp_client = spotipy.Spotify(auth=token_data['access_token'])

    user_playlists = sp_client.current_user_playlists()['items']
    discover_weekly_id = None
    saved_weekly_id = None

    for playlist in user_playlists:
        if playlist['name'] == 'Discover Weekly':
            discover_weekly_id = playlist['id']
        elif playlist['name'] == 'Saved Weekly':
            saved_weekly_id = playlist['id']
    
    if not discover_weekly_id:
        return 'Discover Weekly playlist not located.'
    
    if not saved_weekly_id:
        user_id = sp_client.me()['id']
        saved_playlist = sp_client.user_playlist_create(user_id, 'Saved Weekly', public=False)
        saved_weekly_id = saved_playlist['id']

    discover_weekly_tracks = sp_client.playlist_items(discover_weekly_id)
    track_uris = [track['track']['uri'] for track in discover_weekly_tracks['items']]
    
    sp_client.user_playlist_add_tracks(user_id, saved_weekly_id, track_uris)

    return 'Tracks from Discover Weekly added successfully'

# Function to retrieve token information from the session
def retrieve_token():
    token_data = session.get(TOKEN_KEY, None)
    if not token_data:
        return redirect(url_for('login', _external=False))
    
    current_time = int(time.time())

    if token_data['expires_at'] - current_time < 60:
        oauth = setup_spotify_oauth()
        token_data = oauth.refresh_access_token(token_data['refresh_token'])
        session[TOKEN_KEY] = token_data

    return token_data

# Function to setup Spotify OAuth
def setup_spotify_oauth():
    return SpotifyOAuth(
        client_id='966f6896d45c4449bdd3f275249f5615',
        client_secret='c88ac867e9bc460f97be3cd8268a2ddd',
        redirect_uri=url_for('callback', _external=True),
        scope='user-library-read playlist-modify-public playlist-modify-private'
    )

if __name__ == "__main__":
    app.run(debug=True)
