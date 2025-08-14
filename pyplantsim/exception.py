
class PlantsimException(Exception):
    """Thrown when dispatching the plantsim instance fails"""
    _message: str
    _id: int

    def __init__(self, e: Exception, *args):
        """
        Initializes the Exception instance with a message.
        Attributes:
        ----------
        message : str
            the message
        """
        super().__init__(args)

        self._message = e.args[1]
        self._id = e.args[0]

    def __str__(self):
        return f"Plantsim Message: {self._message} - Plantsim Exception ID: {self._id}."
