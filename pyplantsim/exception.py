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


class SimulationException(Exception):
    """Thrown when there is an error thrown in the simulation run"""

    _method_path: str
    _line_number: int

    def __init__(self, method_path: str, line_number: int):
        """
        Initializes the Exception instance with a message.
        Attributes:
        ----------
        message : str
            the message
        """
        super().__init__()

        self._method_path = method_path
        self._line_number = line_number

    def __str__(self):
        return f"Method {self._method_path} crashed on line {self._line_number}."
