import logging

from .stages import TerminalStage

logger = logging.getLogger(__name__)


class StageController(object):
    """
    Delegates incoming events sent to `event_handler` to the appropriate stage implementation.
    """

    def __init__(self, device):
        self.stages = {}
        self.device = device
        self.active_stage = None
        self.add_stage(TerminalStage)

    def add_stage(self, s):
        if getattr(s, 'NAME') is not None:
            self.stages[s.NAME] = s
            logging.info(f"Adding stage: {s.NAME}")
        else:
            logging.error("Did not add stage as it had no NAME set.")

    def event_handler(self, event, context):
        """
        Display event handler. Will switch active stage if different to current.
        """
        if self.active_stage is not None and event['stage'] != self.active_stage.NAME:
            logging.info(
                "Different stage encountered. Stopping current stage...")
            self.active_stage.stop()
            self.active_stage = None

        if self.active_stage is None:
            next_ctor = self.stages.get(event['stage'], None)
            if next_ctor is not None:
                logging.info(f"Creating and starting stage: {event['stage']}")
                self.active_stage = next_ctor(self.device)
                self.active_stage.start()
            else:
                error = f"Invalid stage: {event['stage']} is not registered."
                logging.error(error)
                self.active_stage = TerminalStage(self.device)
                self.active_stage.handle(
                    {'message': error}, context)
                return
        self.active_stage.handle(event, context)
