import logging
import sys
import os
import json
import redis
import time
from luma.core.virtual import terminal
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from dotenv import load_dotenv
from joedisplay import get_device, StageController
from transport.stages import TrainDepartureBoardStage
from joedisplay.stages import MetricsStage

"""
Demo MQTT driver
"""

load_dotenv()


def create_mqtt_client():
    client = AWSIoTMQTTClient("")
    client.configureEndpoint(os.getenv("AWS_IOT_ENDPOINT"), 8883)
    client.configureCredentials(
        os.getenv("CA"), os.getenv("KEY"), os.getenv("CERT"))
    client.configureAutoReconnectBackoffTime(1, 32, 20)
    # Infinite offline Publish queueing
    client.configureOfflinePublishQueueing(-1)
    client.configureDrainingFrequency(2)  # Draining: 2 Hz
    client.configureConnectDisconnectTimeout(10)  # 10 sec
    client.configureMQTTOperationTimeout(5)  # 5 sec
    return client


logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.ERROR)

device = get_device()

term = terminal(device, None)
term.println(
    f"Display ready for events on MQTT topic:\n{os.getenv('DISPLAY_TOPIC')}.")
term.flush()

controller = StageController(device)
controller.add_stage(TrainDepartureBoardStage)
controller.add_stage(MetricsStage)

if __name__ == "__main__":
    def handler(client, userdata, message):
        event = json.loads(message.payload)
        controller.event_handler(event, {})

    client = create_mqtt_client()
    client.connect()
    client.subscribe(os.getenv("DISPLAY_TOPIC"), 1, handler)

    while True:
        time.sleep(1)

    client.disconnect()
