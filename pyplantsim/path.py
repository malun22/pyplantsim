
class PlantsimPath:
    """
    Create a PlantsimPath

    Attributes:
    ----------
    *entries : str
        The entries to be concatinated together to a path
    """

    path: str = ""

    def __init__(self, *entries: str) -> None:
        path = ""
        for entry in entries:
            path += f".{entry}"

        self.path = path

    def __str__(self) -> str:
        return self.path

    def to_str(self) -> str:
        return str(self)
