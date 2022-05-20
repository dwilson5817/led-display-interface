import os

import flask
import spotipy
from dotenv import load_dotenv
from flask import Flask, flash
from flask import render_template, request, url_for, redirect
from spotipy import SpotifyOAuth, SpotifyOauthError

from utils.commands import run_cmd, is_up
from utils.files import read_value, write_file

app = Flask(__name__)

load_dotenv()

app.secret_key = os.getenv('SESSION_KEY')
app.config['SESSION_TYPE'] = 'filesystem'

spotify_oauth = SpotifyOAuth(scope='user-read-currently-playing')
spotify = spotipy.Spotify(client_credentials_manager=spotify_oauth)

message = read_value('message')


@app.route('/', methods=['GET', 'POST'])
def index():
    global message

    if request.method == "POST":
        req = request.form
        text = req.get("text")

        if not text:
            flash('The message cannot be empty!', 'danger')
            return redirect('/')
        else:
            write_file(message=text)
            message = text

            if is_up():
                flash('The message was saved and will be displayed momentarily!', 'success')
            else:
                flash('The message was saved but the service is currently stopped!', 'warning')

            return redirect('/')

    if spotify_oauth.get_cached_token():
        return render_template('index.html', message=message, is_up=is_up(), spotify=spotify)

    return render_template('index.html', message=message, is_up=is_up())


@app.route('/start', methods=['GET'])
def start():
    return run_cmd(['systemctl', 'start', 'led-display.service'],
                   'Successfully started systemd service!',
                   'Failed to start systemd service!')


@app.route('/stop', methods=['GET'])
def stop():
    return run_cmd(['systemctl', 'stop', 'led-display.service'],
                   'Successfully stopped systemd service!',
                   'Failed to stop systemd service!')


@app.route('/restart', methods=['GET'])
def restart():
    return run_cmd(['systemctl', 'restart', 'led-display.service'],
                   'Successfully restarted systemd service!',
                   'Failed to restart systemd service!')


@app.route('/spotify/connect', methods=['GET'])
def connect():
    try:
        if spotify:
            display_name = spotify.current_user().get('display_name')

            flash(
                'Hello, <strong>{}</strong>!  You account is connected!'.format(display_name),
                'success'
            )
    except SpotifyOauthError as e:
        flash(
            'Failed to connect to your Spotify account.  Got error: {}'.format(e),
            'danger'
        )

    return redirect('/')


@app.route('/spotify/disconnect', methods=['GET'])
def disconnect():
    os.remove(".cache")

    flash('Your account was disconnected!', 'success')
    return redirect('/')


@app.route('/api/message', methods=['GET'])
def get_message():
    return flask.jsonify(message=message)


@app.route('/api/currently_playing', methods=['GET'])
def currently_playing():
    if spotify_oauth.get_cached_token():
        song = spotify.currently_playing().get('item').get('name')
        artists = [ artist['name'] for artist in spotify.currently_playing().get('item').get('album').get('artists') ]

        return flask.jsonify(currently_playing='{} by {}'.format(song, ', '.join(artists)))
    else:
        return flask.jsonify(currently_playing=False)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
