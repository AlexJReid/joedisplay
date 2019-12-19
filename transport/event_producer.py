import json
import boto3
import os
from transport_api import TransportAPI, TrainDisplayBoardDecorator

client = boto3.client('iot-data')

api = TrainDisplayBoardDecorator(TransportAPI(os.environ.get(
    "TRANSPORTAPI_APP_ID"), os.environ.get("TRANSPORTAPI_APP_KEY")))


def load_departures_for_station_handler(event, context):
    data = event['data']
    display_event = api.load_departures_for_station(
        data['station_code'], top=4)
    topic = f"display/{event['client_id']}/input"
    response = client.publish(
        topic=topic,
        qos=1,
        payload=json.dumps(display_event)
    )
