from typing import Union


class PlantsimPath:
    """
    PlantSim path object for handling and concatenating hierarchical object paths.

    :param entries: Entries to be concatenated into a path.
    :type entries: Union[str, PlantsimPath]

    :ivar _path: Internal string representation of the path.
    :vartype _path: str
    """

    _path: str = ""

    def __init__(self, *entries: Union[str, "PlantsimPath"]) -> None:
        """
        Initialize a PlantsimPath by concatenating given entries.

        :param entries: Strings or PlantsimPath objects to build the path.
        :type entries: Union[str, PlantsimPath]
        """
        for entry in entries:
            if isinstance(entry, PlantsimPath):
                entry = str(entry)
            self.append(entry)

    def __str__(self) -> str:
        """
        Return the path as a string.

        :return: Path as string.
        :rtype: str
        """
        return self._path

    def __eq__(self, other):
        """
        Compare two PlantsimPath objects.

        :param other: Object to compare against.
        :type other: Any
        :return: True if paths are equal, False otherwise.
        :rtype: bool
        """
        if not isinstance(other, PlantsimPath):
            return False

        return str(self) == str(other)

    def to_str(self) -> str:
        """
        Return the path as a string.

        :return: Path as string.
        :rtype: str
        """
        return str(self)

    def append(self, entry: str) -> None:
        """
        Append a path entry to the current path.

        :param entry: Path entry to append.
        :type entry: str
        """
        if entry.startswith(".") or entry.startswith("[") or str(self).endswith("."):
            self._path += entry
        else:
            self._path += f".{entry}"
