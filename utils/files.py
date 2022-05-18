import io
import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
filename = Path(os.getenv('JSON_FILE'))


def write_file(message=None, auth_token=None):
    new = {'message': message or read_value('message'),
           'auth_token': auth_token if auth_token is not None else read_value('auth_token')
           }

    with open(filename, 'w') as f:
        json.dump(new, f)


def read_value(value):
    create_file()
    f = open(filename)
    data = json.load(f)
    result = data.get(value, '')
    f.close()
    return result


def create_file():
    if not os.path.isfile(filename) or not os.access(filename, os.R_OK):
        with io.open(filename, 'w') as db_file:
            db_file.write(json.dumps({}))
