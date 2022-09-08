from datetime import datetime, timedelta

from utils.files import read_file, write_file


def get_from_cache(handler):
    update_cache(handler)

    return read_file(handler.get_cache_file_name()).get("Response")


def update_cache(handler):
    file = read_file(handler.get_cache_file_name())
    time_now = datetime.now()

    if "RetrievedAt" in file:
        last_update = datetime.fromtimestamp(file.get("RetrievedAt"))
    else:
        last_update = time_now - (handler.get_cache_max_age() + timedelta(seconds=1))

    if (time_now - last_update) > handler.get_cache_max_age():
        result = handler.send_request()

        if result is not None:
            write_file(handler.get_cache_file_name(), {
                "RetrievedAt": time_now.timestamp(),
                "Response": result
            })
