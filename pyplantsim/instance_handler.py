from pyplantsim import Plantsim
from pyplantsim.licenses import PlantsimLicense
from pyplantsim.versions import PlantsimVersion

from typing import List


class InstanceHandler:
    """
    This class offers to handle multiple pyplantsim instances with the same model at the same time.
    """
    instances: List[Plantsim]
    free_instances: List[Plantsim]

    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_all_instances()

    def __init__(self):
        self.instances = []
        self.free_instances = []

    def create_instances(self, amount_instances: int, version=PlantsimVersion, visible: bool = False, trusted: bool = True,
                         license: PlantsimLicense = PlantsimLicense.STUDENT, suppress_3d: bool = False, show_msg_box: bool = False) -> None:
        """
        Create new instances of pyplantsim.
        """
        for _ in range(amount_instances):
            self.create_instance()

    def close_instance(self, instance: Plantsim) -> None:
        """
        Close an instance of pyplantsim.
        """
        instance.quit()
        self.instances.remove(instance)
        self.free_instances.remove(instance)

    def close_all_instances(self) -> None:
        """
        Closes all instances of pyplantsim.
        """
        for instance in self.instances:
            instance.quit()
        self.instances = []
        self.free_instances = []

    def create_instance(self, version=PlantsimVersion, visible: bool = False, trusted: bool = True,
                        license: PlantsimLicense = PlantsimLicense.STUDENT, suppress_3d: bool = False, show_msg_box: bool = False) -> None:
        """
        Create a new instance of pyplantsim.
        """
        instance = Plantsim(
            version=version,
            visible=visible,
            trusted=trusted,
            license=license,
            suppress_3d=suppress_3d,
            show_msg_box=show_msg_box
        )
        self.instances.append(instance)
        self.free_instances.append(instance)
