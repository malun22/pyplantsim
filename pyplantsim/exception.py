from __future__ import annotations


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

    def __init__(self, e: Exception, *args: object):
        """
        Initialize the PlantsimException instance.

        :param e: The original exception to wrap.
        :type e: Exception
        :param args: Additional arguments for the base Exception.
        :type args: Any
        """
        super().__init__(args)
        self._id: int = e.args[0] if len(e.args) > 0 else -1
        self._message: str = e.args[1] if len(e.args) > 1 else str(e)

    def __str__(self) -> str:
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

    def __init__(self, method_path: str, line_number: int) -> None:
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

    def __str__(self) -> str:
        """
        Return the string representation of the exception.

        :return: String representation with method path and line number.
        :rtype: str
        """
        return f"Method {self._method_path} crashed on line {self._line_number}."


class PlantsimStateException(Exception):
    """Base for state-related errors that don't wrap a COM exception."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self._message = message

    def __str__(self) -> str:
        return self._message


class PlantsimAlreadyRunningException(PlantsimStateException):
    """Raised when start() is called on an already-running instance."""


class PlantsimNotRunningException(PlantsimStateException):
    """Raised when an operation is attempted on a closed instance."""


class ModelAlreadyLoadedException(PlantsimStateException):
    """Raised when load_model() is called while another model is open."""


class ModelNotFoundException(PlantsimStateException):
    """Raised when the model file does not exist."""


class ModelNotLoadedException(PlantsimStateException):
    """Raised when an operation requires a loaded model but none is present."""


class EventControllerNotSetException(PlantsimStateException):
    """Raised when an operation requires the EventController to be set."""


class ErrorHandlerException(PlantsimStateException):
    """Raised when installing or removing the error handler fails."""
