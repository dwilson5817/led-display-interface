import os
from datetime import timedelta
from pathlib import Path


class BaseApiHandler:
    def send_request(self):
        """Send a request to the API"""
        pass

    def return_result(self):
        """Send a request to the API"""
        pass

    def get_cache_max_age(self):
        """Returns the time after which to discard cached data"""
        return timedelta(seconds=10)

    def get_cache_file_name(self):
        """Returns the name of the file to store the cached data in"""
        return Path(os.getenv('JSON_FILE'))
