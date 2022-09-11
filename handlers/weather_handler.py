import os
from datetime import timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

from handlers.base_api_handler import BaseApiHandler
from utils.cache_utils import get_from_cache


class WeatherHandler(BaseApiHandler):
    def __init__(self):
        load_dotenv()

        self.ACCUWEATHER_API_HOST = "dataservice.accuweather.com"
        self.ACCUWEATHER_API_ENDPOINT = "/currentconditions/v1"
        self.ACCUWEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
        self.ACCUWEATHER_LOCATION_ID = os.getenv('WEATHER_LOCATION_ID')

    def send_request(self):
        response = requests.get(
            "https://{}{}/{}?apikey={}".format(self.ACCUWEATHER_API_HOST, self.ACCUWEATHER_API_ENDPOINT,
                                               self.ACCUWEATHER_LOCATION_ID, self.ACCUWEATHER_API_KEY))

        return response.json()[0] if response.status_code == 200 else None

    def return_result(self):
        response = get_from_cache(self)
        temp_c = response.get("Temperature").get("Metric").get("Value")
        weather_text = response.get("WeatherText")

        return "{} and {} degrees Celsius in Belfast".format(weather_text, temp_c)

    def get_cache_max_age(self):
        return timedelta(minutes=30)

    def get_cache_file_name(self):
        return Path(os.getenv('WEATHER_FILE'))
