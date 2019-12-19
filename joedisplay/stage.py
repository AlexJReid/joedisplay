class Stage(object):
    """
    A stage is a screen configuration such as a train times display board or text terminal.
    It is responsible for rendering to the device. It is instantiated with the active device and receives
    messages from subscribed topics. The `stage` property in the event payload determines the stage to use.
    If this differs from the active stage, the active stage is stopped and the new stage is created and started.
    Stages follow a loose interface: they must implement `start(), stop() and handle(event, context)`.
    """

    def start(self):
        pass

    def stop(self):
        pass

    def handle(self, event, context):
        pass
