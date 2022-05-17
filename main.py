import subprocess
from pathlib import Path

from flask import Flask, render_template, request, redirect, flash

app = Flask(__name__)

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'


@app.route('/', methods=['GET', 'POST'])
def index():
    filename = Path('../led_display.txt')
    filename.touch(exist_ok=True)

    with open(filename, 'r') as f:
        current_value = f.readline().rstrip('\n')

        if request.method == "POST":

            req = request.form
            text = req.get("text")

            if not text:
                flash('The message cannot be empty!', 'danger')
                return redirect('/')
            else:
                fw = open(filename, 'w')
                fw.write(text)
                fw.close()
                if is_up():
                    flash('The message was saved and will be displayed momentarily!', 'success')
                else:
                    flash('The message was saved but the service is currently stopped!', 'warning')

                return redirect('/')

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


def is_up():
    stat = subprocess.call(['systemctl', 'is-active', '--quiet', 'led-display'])
    return stat == 0


def run_cmd(cmd, success_message, failure_message):
    command = subprocess.run(cmd)

    if command.returncode:
        flash(failure_message, 'danger')
        return redirect('/')
    else:
        flash(success_message, 'success')
        return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
