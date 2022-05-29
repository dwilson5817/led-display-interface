import os

from dotenv import load_dotenv
from flask import Flask, request, flash, redirect, url_for, render_template, jsonify
from spotipy import CacheFileHandler, SpotifyPKCE, Spotify, SpotifyOauthError

from utils.commands import is_up, run_cmd
from utils.files import read_value, write_file

app = Flask(__name__)

load_dotenv()

app.secret_key = os.getenv('SESSION_KEY')
app.config['SESSION_TYPE'] = 'filesystem'

spotify_cache = CacheFileHandler()
spotify_oauth = SpotifyPKCE(scope='user-read-currently-playing', open_browser=False, cache_handler=spotify_cache)
spotify = Spotify(client_credentials_manager=spotify_oauth)

message = read_value('message')


@app.route('/', methods=['GET', 'POST'])
def index():
    global message

    if request.method == "POST":
        req = request.form
        text = req.get("text")

        if not text:
            flash('The message cannot be empty!', 'danger')
            return redirect(url_for('index'))
        else:
            write_file(message=text)
            message = text

            if is_up():
                flash('The message was saved and will be displayed momentarily!', 'success')
            else:
                flash('The message was saved but the service is currently stopped!', 'warning')

            return redirect(url_for('index'))

    if spotify_oauth.get_cached_token():
        return render_template('index.html', message=message, is_up=is_up(), current_user=spotify.current_user())

    return render_template('index.html', message=message, is_up=is_up())


@app.route('/service/start', methods=['GET'])
def service_start():
    return run_cmd(['systemctl', 'start', 'led-display.service'],
                   'Successfully started systemd service!',
                   'Failed to start systemd service!')


@app.route('/service/stop', methods=['GET'])
def service_stop():
    return run_cmd(['systemctl', 'stop', 'led-display.service'],
                   'Successfully stopped systemd service!',
                   'Failed to stop systemd service!')


@app.route('/service/restart', methods=['GET'])
def service_restart():
    return run_cmd(['systemctl', 'restart', 'led-display.service'],
                   'Successfully restarted systemd service!',
                   'Failed to restart systemd service!')


@app.route('/spotify/connect', methods=['GET'])
def spotify_connect():
    if _is_logged_in():
        flash('An account is already connected!', 'warning')
        return redirect(url_for('index'))

    return redirect(spotify_oauth.get_authorize_url())


@app.route('/spotify/save', methods=['GET'])
def spotify_save():
    if _is_logged_in():
        flash('An account is already connected!', 'warning')
        return redirect(url_for('index'))

    try:
        code = spotify_oauth.parse_response_code(request.url)

        if not code:
            return redirect(url_for('spotify_connect'))

        access_token = spotify_oauth.get_access_token(code=code)
        display_name = spotify.me().get('display_name')

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


@app.route('/spotify/disconnect', methods=['GET'])
def spotify_disconnect():
    os.remove(".cache")

    flash('Your account was disconnected!', 'success')
    return redirect(url_for('index'))


@app.route('/api/message', methods=['GET'])
def api_get_message():
    return jsonify(message=message)


@app.route('/api/currently_playing', methods=['GET'])
def api_currently_playing():
    if _is_logged_in() and spotify.currently_playing():
        song = spotify.currently_playing().get('item').get('name')
        artists = [ artist['name'] for artist in spotify.currently_playing().get('item').get('album').get('artists') ]

        return jsonify(currently_playing='{} by {}'.format(song, ', '.join(artists)))
    else:
        return jsonify(currently_playing=False)


def _is_logged_in():
    return spotify_cache.get_cached_token()


if __name__ == '__main__':
    app.run(host='0.0.0.0')
