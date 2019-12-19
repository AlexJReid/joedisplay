import logging
from luma.core.virtual import terminal
from luma.core.render import canvas
from luma.core.virtual import viewport
import time

from joedisplay.helpers import make_font
from joedisplay import Stage

logger = logging.getLogger(__name__)


class TerminalStage(Stage):
    """
    Simple stage implementation that wraps luma.core's terminal utility.
    Example payload in examples/text.json
    """
    NAME = 'text'

    def __init__(self, device):
        self.term = terminal(device, None)

    def handle(self, event, context):
        self.term.println(event['message'])


class ScrollStage(Stage):
    """
    Scrolling text stage implementation. Borrowed from luma.examples.
    https://github.com/rm-hull/luma.examples
    """
    NAME = 'scroll'

    def __init__(self, device):
        self.device = device

    def scroll_message(self, full_text, font=None, speed=1):
        device = self.device
        x = device.width

        with canvas(device) as draw:
            w, h = draw.textsize(full_text, font)

        virtual = viewport(device, width=max(
            device.width, w + x + x), height=max(h, device.height))
        with canvas(virtual) as draw:
            draw.text((x, 0), full_text, font=font, fill="white")

        i = 0
        while i < x + w:
            virtual.set_position((i, 0))
            i += speed
            time.sleep(0.025)

    def handle(self, event, context):
        font = make_font('FreePixel.ttf', 14)
        self.scroll_message(event['message'], font=font)
