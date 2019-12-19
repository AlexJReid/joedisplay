import os
import requests
import json

"""
Components that make calls to the Transport API and format them into a form understood by 
stage implementations available within the device driver.

For more information about the API used, see
https://developer.transportapi.com/
"""


class TransportAPI(object):
    """
    Client to interact with the UK Transport API.
    """
    class BadRequestException(Exception):
        def __init__(self, message):
            self.message = message

    def __init__(self, app_id, app_key):
        """
        Constructor requires app ID and app key from https://developer.transportapi.com/
        """
        self.app_id = app_id
        self.app_key = app_key

    def load_departures_for_station(self, departure_station_code, calling_at=None):
        """
        Get live departures from `departure_station_code` - a CRS code.
        Optionally only include departures that are calling at `calling_at` - also a CRS code.
        See the API documentation for more information and also this list of stations here:
        http://www.railwaycodes.org.uk/crs/CRS0.shtm
        """
        url = f"https://transportapi.com/v3/uk/train/station/{departure_station_code}/live.json"

        params = {
            'app_id': self.app_id,
            'app_key': self.app_key
        }

        if calling_at:
            params['calling_at'] = calling_at

        r = requests.get(url=url, params=params)

        if r.status_code != 200:
            raise TransportAPI.BadRequestException(r.json().get("error"))
        else:
            return r.json()


class TrainDisplayBoardDecorator(object):
    """
    Decorator for above API client to transform the responses into JSON understood by the train-display-board
    display stage.
    """

    def __init__(self, api):
        self.api = api

    def load_departures_for_station(self, departure_station_code, calling_at=None, platform=None, top=100):
        try:
            if departure_station_code is None:
                raise TransportAPI.BadRequestException(
                    "No departure station code set.")
            data = self.api.load_departures_for_station(
                departure_station_code, calling_at)
            return self.display_payload(data, platform, top)
        except TransportAPI.BadRequestException as e:
            return self.error_payload(e.message)

    def display_payload(self, data, platform, top):
        def status_text(d):
            if d.get('status') == 'CANCELLED':
                return 'Cancelled'
            expected_departure = d.get('expected_departure_time')
            if d.get('aimed_departure_time') == d.get('expected_departure_time'):
                return 'On time'
            elif expected_departure is not None:
                return 'Exp ' + expected_departure

        def platform_text(d):
            plat = d.get('platform', None)
            if plat:
                return 'Plat ' + plat
            return ''

        def xform(d):
            return {
                'departure_time': d.get('aimed_departure_time'),
                'destination': d.get('destination_name'),
                'platform': platform_text(d),
                'status': status_text(d),
                'operator': d.get('operator'),
                'train_uid': d.get('train_uid')
            }

        departures = data['departures']['all']

        # The API does not support filtering by platform, so do it here.
        if platform:
            departures = list(filter(lambda d: d.get(
                'platform') == str(platform), departures))

        # xform and topN the departure list from the API
        transformed_departures = list(map(xform, departures[0:top]))

        return {
            'stage': 'train-display-board',
            'data': {
                'request_time': data.get('request_time'),
                'station_code': data.get('station_code'),
                'station_name': data.get('station_name'),
                'departures': transformed_departures
            }
        }

    def error_payload(self, error):
        return {
            'stage': 'text',
            'message': f"Sorry! An error occurred:\n{error}"
        }


if __name__ == "__main__":
    """
    Dump the 'display' JSON. Set TRANSPORTAPI_APP_ID and TRANSPORTAPI_APP_KEY with credentials from the developer portal.
    """
    api = TrainDisplayBoardDecorator(TransportAPI(os.environ.get(
        "TRANSPORTAPI_APP_ID"), os.environ.get("TRANSPORTAPI_APP_KEY")))
    data = api.load_departures_for_station('NCL', top=4)
    print(json.dumps(data, indent=2))
