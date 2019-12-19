import logging
import sys
import os
import json
import time
from luma.core.virtual import terminal

from dotenv import load_dotenv
from joedisplay import get_device, StageController, IoTDisplayDriver
from transport.stages import TrainDepartureBoardStage
from joedisplay.stages import MetricsStage

load_dotenv()

logging.getLogger("AWSIoTPythonSDK.core").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    client_id = os.getenv("CLIENT_ID")
    display_topic = f"display/{client_id}/input"

    logger.info("Display topic %s", display_topic)

    device = get_device()

    controller = StageController(device)
    controller.add_stage(TrainDepartureBoardStage)
    controller.add_stage(MetricsStage)

    term = terminal(device, None)
    term.println('*** joedisplay ***')

    driver = IoTDisplayDriver(client_id, display_topic, os.getenv(
        "AWS_IOT_ENDPOINT"), os.getenv("CA"), os.getenv("KEY"), os.getenv("CERT"), controller)
    driver.register_text_updates_callback(term.println)

    driver.start()

    while True:
        time.sleep(1)

    driver.stop()
