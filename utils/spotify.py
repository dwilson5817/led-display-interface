import os
import time

from dotenv import load_dotenv
from flask import session, url_for
from spotipy import SpotifyOAuth

TOKEN_INFO = "token_info"

load_dotenv()


class SpotifyNotLoggedInException(Exception):
    """Raised when a user attempts to perform an actions for which they need to be logged into Spotify"""
    pass


def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise SpotifyNotLoggedInException
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
        redirect_uri=url_for('redirectPage', _external=True),
        scope='user-read-currently-playing')
