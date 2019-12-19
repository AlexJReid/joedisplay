import os
import sys
import time
from PIL import ImageFont
from luma.core.render import canvas
from luma.core.virtual import viewport, snapshot, hotspot
from datetime import datetime
from joedisplay.helpers import make_font

"""
Renderers for UK train times.

Heavily influenced by:
- https://github.com/balena-io-playground/UK-Train-Departure-Display
- https://github.com/chrishutchinson/train-departure-screen

Caveats:
- Doesn't yet support the scrolling 'Calling at: ' functionality of the above.
- Probably should think about truncating longer station names
"""

font = make_font("Dot Matrix Regular.ttf", 10)
font_bold = make_font("Dot Matrix Bold.ttf", 10)
font_bold_tall = make_font("Dot Matrix Bold Tall.ttf", 10)
font_bold_large = make_font("Dot Matrix Bold.ttf", 20)


class DepartureRenderer(hotspot):
    """
    Renders a line (i.e. a departure) on the display board.
    Contains state. Updates only if the `dirty` flag is high.
    """

    def __init__(self, width, height, title_font, font):
        super(DepartureRenderer, self).__init__(width, height)
        self.width = width
        self.height = height
        self.title_font = title_font
        self.font = font
        # State
        self.departure_time = None
        self.destination = None
        self.platform = None
        self.status = None
        # Should refresh?
        self.dirty = False

    def set_dirty(self, b):
        self.dirty = b

    def clear(self):
        self.departure_time = ""
        self.destination = ""
        self.platform = ""
        self.status = ""

    def should_redraw(self):
        # Don't show if not yet initialised
        if self.departure_time is None or self.destination is None or self.platform is None or self.status is None:
            return False
        if self.dirty:
            self.dirty = False
            return True
        return False

    def update(self, draw):
        # Get max widths - shouldn't actually need to measure every time?
        w, h = draw.textsize("Exp 00:00", self.font)
        sw, sh = draw.textsize(self.status, self.font)
        pw, ph = draw.textsize("Plat 88", self.font)
        tw, th = draw.textsize("00:00", self.title_font)

        draw.text((0, 0), self.departure_time, font=self.title_font)
        draw.text((tw + 4, 0), self.destination, font=self.title_font)
        draw.text((self.width - pw - w, 0), self.platform, font=self.font)
        draw.text((self.width - sw, 0), self.status, font=self.font)


class TrainDepartureBoard(object):
    """
    Helper class that renders 4 departures and a clock.
    """

    def __init__(self, device):
        self.DEPARTURE_TOP_MARGIN = 2
        self.DEPARTURE_HEIGHT = 10

        self.viewport = viewport(
            device, width=device.width, height=device.height)

        # Add departure rows. First row has larger title text.
        self.departures = [
            DepartureRenderer(
                device.width, self.DEPARTURE_HEIGHT, font_bold, font),
            DepartureRenderer(device.width, self.DEPARTURE_HEIGHT, font, font),
            DepartureRenderer(device.width, self.DEPARTURE_HEIGHT, font, font),
            DepartureRenderer(device.width, self.DEPARTURE_HEIGHT, font, font)
        ]
        h = 0
        for d in self.departures:
            self.viewport.add_hotspot(d, (0, h))
            h = h + d.height + self.DEPARTURE_TOP_MARGIN

        # Add clock
        self.viewport.add_hotspot(
            snapshot(device.width, 14, self.render_clock, interval=0.1), (0, 50))

    def update(self, departure_data):
        # Empty out current values in case this payload doesn't have the same number of departures
        for renderer in self.departures:
            renderer.clear()

        # Update with passed data
        for renderer, departure in zip(self.departures, departure_data):
            renderer.departure_time = departure.get('departure_time')
            renderer.destination = departure.get('destination')
            renderer.platform = departure.get('platform')
            renderer.status = departure.get('status')

        # Set dirty flag on all to trigger a refresh
        for renderer in self.departures:
            renderer.set_dirty(True)

    def render_clock(self, draw, width, height):
        raw_time = datetime.now().time()
        hour, minute, second = str(raw_time).split('.')[0].split(':')

        w1, h1 = draw.textsize("{}:{}".format(hour, minute), font_bold_large)
        w2, h2 = draw.textsize(":00", font_bold_tall)

        draw.text(((width - w1 - w2) / 2, 0), text="{}:{}".format(hour, minute),
                  font=font_bold_large)
        draw.text((((width - w1 - w2) / 2) + w1, 5), text=":{}".format(second),
                  font=font_bold_tall)

    def refresh(self):
        self.viewport.refresh()
