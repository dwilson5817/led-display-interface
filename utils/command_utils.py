import subprocess
from os import getenv

from flask import flash, redirect


def is_up():
    if getenv('DEVELOPMENT', False):
        return True
    else:
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
