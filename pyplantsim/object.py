from enum import Enum
from pyplantsim import PlantsimPath, Plantsim
from dataclasses import dataclass


class MaterialflowObjects(Enum):
    CONNECTOR = ".Materialflow.Connector"
    EVENT_CONTROLLER = ".Materialflow.EventController"


@dataclass
class PlantsimObject:
    _path: PlantsimPath
    _source_instance: Plantsim

    def set_value(self, attribute: str, value: any):
        self._source_instance.set_value(
            PlantsimPath(self._path, attribute), value)

    def delete(self):
        ...

    def get_value(self, attribute: str) -> any:
        return self._source_instance.get_value(PlantsimPath(self._path, attribute))
