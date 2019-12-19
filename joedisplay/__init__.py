from .stage import Stage
from .controller import StageController
from .device import get_device
from .iot_driver import IoTDisplayDriver

import logging

logging.getLogger('PIL').setLevel(logging.ERROR)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)-15s - %(message)s'
)
