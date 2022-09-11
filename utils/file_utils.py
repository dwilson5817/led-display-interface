import io
import json
import os


def write_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)


def read_file(filename):
    create_file(filename)
    f = open(filename)
    return json.load(f)


def create_file(filename):
    if not os.path.isfile(filename) or not os.access(filename, os.R_OK):
        with io.open(filename, 'w') as db_file:
            db_file.write(json.dumps({}))
