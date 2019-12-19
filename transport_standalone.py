import logging
import sys
import os
import json
from threading import Timer
from luma.core.virtual import terminal

from dotenv import load_dotenv

from joedisplay import get_device, StageController
from transport.stages import TrainDepartureBoardStage
from transport.transport_api import TransportAPI, TrainDisplayBoardDecorator

"""
Standalone train departures board running in a single process.

Required environment variables:
- `TRANSPORTAPI_APP_ID` - Transport API app ID
- `TRANSPORTAPI_APP_KEY` - Transport API app key
- `DEPATURE_STATION` - CRS code of station to show

Data will be refreshed every 30 seconds.
"""

load_dotenv()

REFRESH_INTERVAL_SECONDS = 30

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

device = get_device()

term = terminal(device, None)
term.println('Please wait, loading data...')
term.flush()

controller = StageController(device)
controller.add_stage(TrainDepartureBoardStage)

api = TrainDisplayBoardDecorator(TransportAPI(os.environ.get(
    "TRANSPORTAPI_APP_ID"), os.environ.get("TRANSPORTAPI_APP_KEY")))


def load_data_and_update_display():
    logger.info("Refreshing...")
    event = api.load_departures_for_station(
        os.environ.get("DEPARTURE_STATION"), top=4)
    controller.event_handler(event, None)

    # Schedule refresh every `REFRESH_INTERVAL_SECONDS`
    Timer(REFRESH_INTERVAL_SECONDS, load_data_and_update_display).start()


if __name__ == "__main__":
    load_data_and_update_display()
