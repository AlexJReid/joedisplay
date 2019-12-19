import logging
import os
import json
import time
from threading import Timer
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient, AWSIoTMQTTShadowClient

logger = logging.getLogger(__name__)

"""
Handles display bootstrap and on-going requests for data. See awsiot_display.py for example use.

Discussed more in `AWSIOT.md`

- Request shadow to establish state
- Send a data request to `display/producers/<stage name>` containing context from shadow at a timed interval
- Listen for
    - Display events (and send them to provided `StageController`)
    - Deltas to shadow and apply them to current state
"""


class IoTDisplayDriver(object):
    REFRESH_INTERVAL = 60

    def __init__(self, client_id, display_topic, endpoint, ca, key, cert, stage_controller):
        self.client_id = client_id
        self.display_topic = display_topic
        self.stage_controller = stage_controller

        self.refresh_timer = None
        self.show_text_cb = None
        self.state = {}

        client = AWSIoTMQTTClient(client_id)
        client.configureEndpoint(endpoint, 8883)
        client.configureCredentials(ca, key, cert)
        client.configureAutoReconnectBackoffTime(1, 32, 20)
        client.configureOfflinePublishQueueing(0)
        client.configureDrainingFrequency(2)  # Draining: 2 Hz
        client.configureConnectDisconnectTimeout(10)  # 10 sec
        client.configureMQTTOperationTimeout(5)  # 5 sec
        self.client = client
        self.shadow_client = AWSIoTMQTTShadowClient(
            self.client_id, awsIoTMQTTClient=client)

    def show_text(self, text):
        if self.show_text_cb:
            logger.debug("echo to device: %s", text)
            self.show_text_cb(text)

    def register_text_updates_callback(self, cb):
        self.show_text_cb = cb

    def send_data_request(self):
        logger.info('Pumping data')
        command = {
            'client_id': self.client_id,
            'data': self.state.get('data', {})
        }
        self.client.publishAsync(
            f"display/producers/{self.state['stage']}", json.dumps(command), QoS=1, ackCallback=None)

        self.refresh_timer = Timer(
            self.REFRESH_INTERVAL, self.send_data_request)
        self.refresh_timer.start()

    def on_shadow_response(self, payload_s, status, token):
        logger.info('Got shadow response')
        payload = json.loads(payload_s)
        if status == 'rejected':
            self.show_text(
                'Hello, new device!!!\nGo to the app to display something.')
            return
        elif status == 'accepted':
            self.show_text('Got device shadow.')
            self.state = payload['state']['reported']
            self.refresh_timer = Timer(1, self.send_data_request)
            self.refresh_timer.start()

    def on_shadow_delta(self, payload_s, status, token):
        logger.info('Got shadow update')
        self.cancel_refresh_timer()
        payload = json.loads(payload_s)
        delta = payload['state']
        if delta.get('stage'):
            self.state['data'] = {}

        self.state.update(delta)

        def _update_shadow_callback(payload, status, token):
            logger.info("Updated shadow: %s", status)

        logger.info('Acknowledging shadow update.')
        self.shadow_handler.shadowUpdate(json.dumps({
            'state': {
                'reported': self.state
            }
        }), _update_shadow_callback, 10)

        self.refresh_timer = Timer(1, self.send_data_request)
        self.refresh_timer.start()

    def on_display_event(self, client, userdata, message):
        logger.info('Got display event')
        event = json.loads(message.payload)
        self.stage_controller.event_handler(event, {})

    def start(self):
        self.show_text('Starting...')
        self.client.connect()

        self.shadow_handler = self.shadow_client.createShadowHandlerWithName(
            self.client_id, False)

        self.show_text('Fetching shadow...')
        self.shadow_handler.shadowGet(self.on_shadow_response, 15)
        self.shadow_handler.shadowRegisterDeltaCallback(self.on_shadow_delta)

        self.client.subscribe(self.display_topic, 1, self.on_display_event)

    def cancel_refresh_timer(self):
        if self.refresh_timer:
            self.refresh_timer.cancel()
            self.refresh_timer = None

    def stop(self):
        self.cancel_refresh_timer()
        self.client.disconnect()
