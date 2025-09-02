class InstanceHandlerNotInitializedException(Exception):
    """
    Exception raised when an operation is attempted on an instance
    that has not been initialized.

    :param message: Error message describing the exception.
    :type message: str
    :param args: Additional arguments for the base Exception.
    :type args: Any

    :ivar _message: Error message for the missing initialization exception.
    :vartype _message: str
    """

    _message: str

    def __init__(self, message: str = "Instance has not been initialized.", *args):
        """
        Initialize the InstanceNotInitializedException instance.

        :param message: Error message to display.
        :type message: str
        :param args: Additional arguments for the base Exception.
        :type args: Any
        """
        super().__init__(message, *args)
        self._message = message

    def __str__(self):
        """
        Return the string representation of the exception.

        :return: String representation with the error message.
        :rtype: str
        """
        return f"InstanceNotInitializedException: {self._message}"
