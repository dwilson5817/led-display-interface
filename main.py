import os

import spotipy
from dotenv import load_dotenv
from flask import Flask, flash
from flask import render_template, request, url_for, session, redirect

import utils.spotify
from utils.commands import run_cmd, is_up
from utils.files import read_value, write_file
from utils.spotify import create_spotify_oauth, get_token

app = Flask(__name__)

load_dotenv()

app.secret_key = os.getenv('SESSION_KEY')
app.config['SESSION_TYPE'] = 'filesystem'


@app.route('/', methods=['GET', 'POST'])
def index():
    current_value = read_value('message')
    auth_token = read_value('auth_token')

    if request.method == "POST":

        req = request.form
        text = req.get("text")

        if not text:
            flash('The message cannot be empty!', 'danger')
            return redirect('/')
        else:
            write_file(message=text)
            if is_up():
                flash('The message was saved and will be displayed momentarily!', 'success')
            else:
                flash('The message was saved but the service is currently stopped!', 'warning')

            return redirect('/')
    print(auth_token)
    if auth_token:
        print(auth_token)
        spotify = spotipy.Spotify(auth=auth_token)
        return render_template('index.html', current_value=current_value, is_up=is_up(), spotify=spotify)
    else:
        return render_template('index.html', current_value=current_value, is_up=is_up())


@app.route('/start', methods=['GET'])
def start():
    return run_cmd(['systemctl', '-l', 'start', 'led-display'],
                   'Successfully started systemd service!',
                   'Failed to start systemd service!')


@app.route('/stop', methods=['GET'])
def stop():
    return run_cmd(['systemctl', '-l', 'stop', 'led-display'],
                   'Successfully stopped systemd service!',
                   'Failed to stop systemd service!')


@app.route('/restart', methods=['GET'])
def restart():
    return run_cmd(['systemctl', '-l', 'restart', 'led-display'],
                   'Successfully restarted systemd service!',
                   'Failed to restart systemd service!')


@app.route('/spotify/connect', methods=['GET'])
def connect():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/spotify/disconnect', methods=['GET'])
def disconnect():
    write_file(auth_token='')

    flash('Your account was disconnected!', 'success')
    return redirect('/')


@app.route('/spotify/redirect', methods=['GET'])
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[utils.spotify.TOKEN_INFO] = token_info
    return redirect(url_for('write_auth', _external=True))


@app.route("/spotify/save")
def write_auth():
    try:
        auth_token = get_token().get('access_token')
    except utils.spotify.SpotifyNotLoggedInException:
        return redirect(url_for('connect', _external=False))

    write_file(auth_token=auth_token)

    current_user = spotipy.Spotify(auth=auth_token).current_user()

    flash('Hello, <strong>{}</strong>!  Your Spotify account is now connected and your current song will be displayed '
          'soon!'.format(current_user.get('display_name')), 'success')

    return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
