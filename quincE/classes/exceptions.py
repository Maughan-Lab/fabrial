class FatalSequenceError(BaseException):
    """A non-recoverable error for the sequence."""

    def __init__(self, error_message: str):
        BaseException.__init__(self)
        self.error_message = error_message


class PluginError(Exception):
    """An error caused by a faulty plugin."""
