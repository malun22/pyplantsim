from typing import Union


class PlantsimPath:
    """
    Create a PlantsimPath

    Attributes:
    ----------
    *entries : str | PlantsimPath
        The entries to be concatinated together to a path
    """

    path: str = ""

    def __init__(self, *entries: str) -> None:
        """Initialize a path"""
        path = ""
        for entry in entries:
            append = entry
            if isinstance(append, PlantsimPath):
                append = str(append)

            if append.startswith("."):
                path += append
            else:
                path += f".{append}"

        self.path = path

    def __str__(self) -> str:
        """Returns the path as a string"""
        return self.path

    def __eq__(self, other):
        """Compares two PlantsimPath objects"""
        if not isinstance(other, PlantsimPath):
            return False

        return str(self) == str(other)

    def to_str(self) -> str:
        """Returns the path as a string"""
        return str(self)

    def append(self, entry: str) -> None:
        """Appends a path entry"""
        if entry.startswith(".") or str(self).endswith("."):
            self.path += entry
        else:
            self.path += f".{entry}"
