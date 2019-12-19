import logging
import sys
import os
import json
import redis
import time
from luma.core.virtual import terminal
from subprocess import check_output

from joedisplay import get_device, StageController
from transport.stages import TrainDepartureBoardStage
from joedisplay.stages import MetricsStage

"""
Display exposed as an Redis channel subscriber. Will render any `Stage` registered within the controller.

Any stage registered below with `add_stage` will work.

PUBLISH display-input '{"stage": "text", "message": "Hello from Redis."}'
"""

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

redis_host = os.environ.get('REDIS_HOST', 'localhost')
display_topic = os.environ.get('DISPLAY_CHANNEL', 'display-input')

device = get_device()

term = terminal(device, None)
term.println(
    f"Display ready for events on channel:\n{display_topic}\nRedis host: {redis_host}")
term.flush()

controller = StageController(device)
controller.add_stage(TrainDepartureBoardStage)
controller.add_stage(MetricsStage)

if __name__ == "__main__":
    # Subscribe to Redis topic for display updates
    r = redis.Redis(host=redis_host, port=6379, db=0)
    p = r.pubsub(ignore_subscribe_messages=True)
    p.subscribe(display_topic)

    logger.info(f"Waiting for display events on {display_topic}...")
    while True:
        message = p.get_message()
        if message is not None:
            try:
                event = json.loads(message['data'])
                controller.event_handler(event, None)
            except Exception as e:
                logger.exception(e)
        time.sleep(0.025)
