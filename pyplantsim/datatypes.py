from __future__ import annotations

from datetime import timedelta
from enum import Enum
from typing import Dict


class PlantsimDatatypes(Enum):
    TIME = "time"  # timedelta
    INTEGER = "integer"  # int
    DATETIME = "datetime"  # datetime
    ACCELERATION = "acceleration"
    ARRAY = "array"
    BOOLEAN = "boolean"  # bool
    DATE = "date"  # date
    JSON = "json"  # json
    LENGTH = "length"  # float
    LIST = "list"  # list
    LISTRANGE = "listrange"
    OBJECT = "object"
    QUEUE = "queue"  # list
    REAL = "real"  # float
    SPEED = "speed"  # float
    STACK = "stack"
    STRING = "string"  # str
    TABLE = "table"
    WEIGHT = "weight"  # float


class PlantsimDatatype:
    """Parent class for specific datatypes"""

    def to_plant(self):
        pass

    @staticmethod
    def from_plant() -> PlantsimDatatype:
        pass

    @staticmethod
    def convert_enum_to_plantsim_datatype(enum: PlantsimDatatypes) -> PlantsimDatatype:
        if enum not in enum_class_switch:
            raise Exception(
                f"The given datatype can not be handled. Given: {enum}")

        return enum_class_switch[enum]


class PlantsimTime(timedelta, PlantsimDatatype):
    """Abstraction class for plantsim time datatype"""

    def to_plant(self):
        return self.total_seconds()

    @staticmethod
    def from_plant(value: float) -> PlantsimTime:
        return PlantsimTime(seconds=value)


enum_class_switch: Dict[PlantsimDatatype] = {
    PlantsimDatatypes.TIME: PlantsimTime
}
