import subprocess
from pathlib import Path

from flask import Flask, render_template, request, redirect, flash

app = Flask(__name__)


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
                flash('The message was saved and will be displayed momentarily.', 'success')
                return redirect('/')

        return render_template('index.html', current_value=current_value)


@app.route('/restart', methods=['GET'])
def restart_controller():
    command = subprocess.run(['systemctl', 'restart', 'led-display.service'])

    if command.returncode:
        flash('An error occurred: {}'.format(command.stderr), 'danger')
        return redirect('/')
    else:
        flash('The controller systemd service was restarted successfully.  Output: {}'.format(command.stdout), 'success')
        return redirect('/')


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.run(host='0.0.0.0')
