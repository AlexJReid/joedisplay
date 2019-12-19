from threading import Thread
from luma.core.virtual import terminal
from luma.core.render import canvas
from luma.core.virtual import viewport
import time
import logging
import sys
import json
from threading import Timer

from joedisplay import Stage

from transport.train_renderer import TrainDepartureBoard

logger = logging.getLogger(__name__)


class TrainDepartureBoardStage(Stage):
    NAME = 'train-display-board'

    """
    UK train times display stage implementation. Example payload in examples/train-display-board.json

    Displays 4 rows of depatures of format:

    00:00  Edinburgh Waverley        Plat 2    On time
    00:00  Edinburgh Waverley        Plat 2    On time
    00:00  Edinburgh Waverley        Plat 2    On time
    00:00  Edinburgh Waverley        Plat 2    On time
                      20:00:00

    The clock is refreshed every second.
    """
    class Runner(Thread):
        """
        As this stage displays a clock, we need to constantly be refreshing the display.
        """

        def __init__(self, *args, **kwargs):
            super(TrainDepartureBoardStage.Runner,
                  self).__init__(*args, **kwargs)
            self.aborted = False

        def run(self):
            while not self.aborted:
                self.display.refresh()
                time.sleep(0.025)

    def __init__(self, device):
        self.display = TrainDepartureBoard(device)
        self.runner = TrainDepartureBoardStage.Runner()
        self.runner.display = self.display  # FIX THIS by updating the ctor

    def start(self):
        self.runner.start()

    def stop(self):
        self.runner.aborted = True

    def handle(self, event, context):
        try:
            self.display.update(event['data']['departures'])
        except:
            pass
