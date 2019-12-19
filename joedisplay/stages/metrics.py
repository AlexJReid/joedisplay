import logging
from luma.core.virtual import terminal
from luma.core.render import canvas
from luma.core.virtual import viewport, snapshot, hotspot
import time

from joedisplay.helpers import make_font
from joedisplay import Stage


class MetricRenderer(hotspot):
    def __init__(self, width, height, title_font, font):
        super(MetricRenderer, self).__init__(width, height)
        self.width = width
        self.height = height
        self.title_font = title_font
        self.font = font
        # State
        self.value = None
        self.label = None
        self.dirty = False

    def set_dirty(self, b):
        self.dirty = b

    def clear(self):
        self.value = ""
        self.label = ""

    def should_redraw(self):
        if self.value is None:
            return False
        if self.dirty:
            self.dirty = False
            return True
        return False

    def update(self, draw):
        w, h = draw.textsize(self.value, self.title_font)
        lw, lh = draw.textsize(self.label, self.font)
        offset = (self.width - w) // 2
        label_offset = (self.width - lw) // 2
        draw.text((offset, 0), self.value, font=self.title_font)
        draw.text((label_offset, h + 4), self.label, font=self.font)


class MetricsStage(Stage):
    NAME = 'metrics'

    def __init__(self, device):
        self.viewport = viewport(
            device, width=device.width, height=device.height + 10)

        #font_bold = make_font("OpenSans-Bold.ttf", 28)
        font = make_font("OpenSans-Regular.ttf", 9)
        font_bold = make_font("Slackey-Regular.ttf", 28)
        #font = make_font("Slackey-Regular.ttf", 9)

        metric_width = int(device.width / 4)

        self.metrics = [
            MetricRenderer(metric_width, device.height, font_bold, font),
            MetricRenderer(metric_width, device.height, font_bold, font),
            MetricRenderer(metric_width, device.height, font_bold, font),
            MetricRenderer(metric_width, device.height, font_bold, font)
        ]

        w = 0
        for m in self.metrics:
            self.viewport.add_hotspot(m, (w, 10))
            w = w + m.width

    def update(self, metric_data):
        for renderer in self.metrics:
            renderer.clear()
        for renderer, metric in zip(self.metrics, metric_data):
            renderer.value = metric.get('value')
            renderer.label = metric.get('label')
        for renderer in self.metrics:
            renderer.set_dirty(True)

    def refresh(self):
        self.viewport.refresh()

    def handle(self, event, context):
        self.update(event['metrics'])
        self.refresh()
