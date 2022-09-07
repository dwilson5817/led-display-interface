import io
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()
filename = Path(os.getenv('WEATHER_FILE'))

API_HOST = "dataservice.accuweather.com"
API_ENDPOINT = "/currentconditions/v1"
LOCATION_ID = os.getenv('WEATHER_LOCATION_ID')
API_KEY = os.getenv('WEATHER_API_KEY')


def get_weather():
    print(os.getcwd())
    update_weather()
    weather = read_file().get("Response")

    temp_c = weather.get("Temperature").get("Metric").get("Value")
    weather_text = weather.get("WeatherText")

    return "{} and {} degrees Celsius in Belfast currently".format(weather_text, temp_c)


def update_weather():
    file = read_file()
    time_now = datetime.now()

    if "RetrievedAt" in file:
        last_update = datetime.fromtimestamp(file.get("RetrievedAt"))
    else:
        last_update = time_now - timedelta(minutes=30, seconds=1)

    if (time_now - last_update) > timedelta(minutes=30):
        response = requests.get("https://{}{}/{}?apikey={}".format(API_HOST, API_ENDPOINT, LOCATION_ID, API_KEY))

        if response.status_code == 200:
            write_file({
                "RetrievedAt": time_now.timestamp(),
                "Response": response.json()[0]
            })


def write_file(data):
    with open(filename, 'w') as f:
        json.dump(data, f)


def read_file():
    create_file()
    f = open(filename)
    return json.load(f)


def create_file():
    if not os.path.isfile(filename) or not os.access(filename, os.R_OK):
        with io.open(filename, 'w') as db_file:
            db_file.write(json.dumps({}))
