import logging
import sys
import os
import json
from threading import Timer
from luma.core.virtual import terminal
from subprocess import check_output

from joedisplay import get_device, StageController
from joedisplay.api import create_api
from joedisplay.stages import MetricsStage
from transport.stages import TrainDepartureBoardStage

"""
Display exposed as an HTTP endpoint. Will render any `Stage` registered within the controller.

Any stage registered below with `add_stage` will work. Draw will block the request, unless the stage
implementation runs in its own thread.

curl -X POST \
  http://192.168.1.35:5000/display \
  -H 'Content-Type: application/json' \
  -d '{
    "stage": "text",
    "message": "I was sent to the display through an API."
}'
"""

port = int(os.environ.get('PORT', 5000))

ip = '0.0.0.0'
try:
    # Not portable! But should be OK on RPi.
    ip = check_output(['hostname', '--all-ip-addresses']
                      ).decode().replace(' \n', '')
except:
    pass

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

device = get_device()

term = terminal(device, None)
term.println(
    f"Display ready for POST requests to:\nhttp://{ip}:{port}/display")
term.flush()

controller = StageController(device)
controller.add_stage(TrainDepartureBoardStage)
controller.add_stage(MetricsStage)

api = create_api("example_display_api", controller)

if __name__ == "__main__":
    api.run(host="0.0.0.0", port=port, debug=False)
