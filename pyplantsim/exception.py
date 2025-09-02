class PlantsimException(Exception):
    """
    Exception raised when dispatching the Plant Simulation instance fails.

    :param e: The original exception.
    :type e: Exception
    :param args: Additional arguments for the base Exception.
    :type args: Any

    :ivar _message: Error message from the Plant Simulation exception.
    :vartype _message: str
    :ivar _id: Error ID from the Plant Simulation exception.
    :vartype _id: int
    """

    _message: str
    _id: int

    def __init__(self, e: Exception, *args):
        """
        Initialize the PlantsimException instance.

        :param e: The original exception to wrap.
        :type e: Exception
        :param args: Additional arguments for the base Exception.
        :type args: Any
        """
        super().__init__(args)
        self._message = e.args[1]
        self._id = e.args[0]

    def __str__(self):
        """
        Return the string representation of the exception.

        :return: String representation with message and exception ID.
        :rtype: str
        """
        return f"Plantsim Message: {self._message} - Plantsim Exception ID: {self._id}."


class SimulationException(Exception):
    """
    Exception raised when there is an error during the simulation run.

    :param method_path: Path of the method where the error occurred.
    :type method_path: str
    :param line_number: Line number where the error occurred.
    :type line_number: int

    :ivar _method_path: Path to the method that caused the error.
    :vartype _method_path: str
    :ivar _line_number: Line number where the exception occurred.
    :vartype _line_number: int
    """

    _method_path: str
    _line_number: int

    def __init__(self, method_path: str, line_number: int):
        """
        Initialize the SimulationException instance.

        :param method_path: Path of the method where the error occurred.
        :type method_path: str
        :param line_number: Line number where the error occurred.
        :type line_number: int
        """
        super().__init__()
        self._method_path = method_path
        self._line_number = line_number

    def __str__(self):
        """
        Return the string representation of the exception.

        :return: String representation with method path and line number.
        :rtype: str
        """
        return f"Method {self._method_path} crashed on line {self._line_number}."
