class FatalSequenceError(BaseException):
    """A non-recoverable error for the sequence."""

    def __init__(self, error_message: str):
        BaseException.__init__(self)
        self.error_message = error_message


class StepCancellation(BaseException):
    """
    An exception used to cancel a step. This does not cancel the whole sequence, so it is safe for
    use in a `SequenceStep`.
    """


class PluginError(Exception):
    """An error caused by a faulty plugin."""
