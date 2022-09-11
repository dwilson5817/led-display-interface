import os
from datetime import timedelta

from flask import flash, redirect, url_for
from spotipy import CacheFileHandler, SpotifyPKCE, Spotify, SpotifyOauthError

from handlers.base_api_handler import BaseApiHandler
from utils.cache_utils import get_from_cache
from utils.file_utils import read_file


class SpotifyHandler(BaseApiHandler):
    def __init__(self):
        self._spotify_cache = CacheFileHandler()
        self._spotify_oauth = SpotifyPKCE(scope='user-read-currently-playing', open_browser=False,
                                          cache_handler=self._spotify_cache)
        self._spotify = Spotify(client_credentials_manager=self._spotify_oauth)

    def connect_account(self):
        if self._is_logged_in():
            flash('An account is already connected!', 'warning')
            return redirect(url_for('index'))

        return redirect(self._spotify_oauth.get_authorize_url())

    def disconnect_account(self):
        os.remove(".cache")

        flash('Your account was disconnected!', 'success')
        return redirect(url_for('index'))

    def save_account(self, request):
        if self._is_logged_in():
            flash('An account is already connected!', 'warning')
            return redirect(url_for('index'))

        try:
            code = self._spotify_oauth.parse_response_code(request.url)

            if not code:
                return redirect(url_for('spotify_connect'))

            access_token = self._spotify_oauth.get_access_token(code=code)
            display_name = self._spotify.me().get('display_name')

            if access_token:
                flash(
                    'Hello, <strong>{}</strong>!  You account is connected!'.format(display_name),
                    'success'
                )
            else:
                flash(
                    'Failed to connect to your Spotify account.',
                    'danger'
                )

        except SpotifyOauthError as e:
            flash(
                'Failed to connect to your Spotify account.  {}'.format(e),
                'danger'
            )

        return redirect(url_for('index'))

    def is_logged_in(self):
        return self._spotify_oauth.get_cached_token()

    def get_current_username(self):
        return self._spotify.current_user()

    def send_request(self):
        if self._is_logged_in() and self._spotify.currently_playing():
            return self._spotify.currently_playing()
        else:
            return False

    def return_result(self):
        response = get_from_cache(self)

        if response:
            song = response.get('item').get('name')
            artists = [artist['name'] for artist in response.get('item').get('album').get('artists')]

            return '{} by {}'.format(song, ', '.join(artists))
        else:
            return False

    def get_cache_max_age(self):
        cached_result = read_file(self.get_cache_file_name()).get("Response")

        if cached_result:
            time_remaining = cached_result.get("item").get("duration_ms") - cached_result.get("progress_ms")

            return min(super().get_cache_max_age(), timedelta(milliseconds=time_remaining))

        return super().get_cache_max_age()

    def _is_logged_in(self):
        return self._spotify_cache.get_cached_token()
