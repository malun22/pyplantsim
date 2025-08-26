from typing import Union


class PlantsimPath:
    """
    Create a PlantsimPath

    Attributes:
    ----------
    *entries : Union[str, PlantsimPath]
        The entries to be concatinated together to a path
    """

    _path: str = ""

    def __init__(self, *entries: Union[str, "PlantsimPath"]) -> None:
        """Initialize a path"""
        for entry in entries:
            if isinstance(entry, PlantsimPath):
                entry = str(entry)
            self.append(entry)

    def __str__(self) -> str:
        """Returns the path as a string"""
        return self._path

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
        if entry.startswith(".") or entry.startswith("[") or str(self).endswith("."):
            self._path += entry
        else:
            self._path += f".{entry}"
