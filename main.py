import os

from dotenv import load_dotenv
from flask import Flask, request, flash, redirect, url_for, render_template, jsonify

from utils.api_utils import SpotifyHandler, WeatherHandler
from utils.commands import is_up, run_cmd
from utils.message import read_value, write_file

app = Flask(__name__)

load_dotenv()

app.secret_key = os.getenv('SESSION_KEY')
app.config['SESSION_TYPE'] = 'filesystem'

message = read_value('message')

spotify_handler = SpotifyHandler()
weather_handler = WeatherHandler()


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

    if spotify_handler.is_logged_in():
        return render_template('index.html', message=message, is_up=is_up(),
                               current_user=spotify_handler.get_current_username())

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
    return spotify_handler.connect_account()


@app.route('/spotify/save', methods=['GET'])
def spotify_save():
    return spotify_handler.save_account(request)


@app.route('/spotify/disconnect', methods=['GET'])
def spotify_disconnect():
    return spotify_handler.disconnect_account()


@app.route('/api/message', methods=['GET'])
def api_get_message():
    return jsonify(message=message)


@app.route('/api/weather', methods=['GET'])
def api_get_weather():
    return jsonify(message=weather_handler.return_result())


@app.route('/api/currently_playing', methods=['GET'])
def api_currently_playing():
    return jsonify(message=spotify_handler.return_result())


if __name__ == '__main__':
    app.run(host='0.0.0.0')
