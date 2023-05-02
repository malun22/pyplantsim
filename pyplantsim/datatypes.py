from __future__ import annotations

from datetime import timedelta, date, datetime
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


class PlantsimDateTime(datetime, PlantsimDatatype):
    """Abstraction class for plantsim datetime datatype"""

    def to_plant(self):
        ...

    @staticmethod
    def from_plant(value) -> PlantsimDateTime:
        ...


class PlantsimAcceleration(float, PlantsimDatatype):
    """Abstraction class for plantsim acceleration datatype"""

    def to_plant(self):
        ...

    @staticmethod
    def from_plant(value) -> PlantsimDateTime:
        ...


class PlantsimArray(list, PlantsimDatatype):
    """Abstraction class for plantsim array datatype"""

    def to_plant(self):
        ...

    @staticmethod
    def from_plant(value) -> PlantsimDateTime:
        ...


class PlantsimBoolean(int, PlantsimDatatype):
    """Abstraction class for plantsim boolean datatype"""

    def to_plant(self):
        ...

    @staticmethod
    def from_plant(value) -> PlantsimDateTime:
        ...


class PlantsimDate(date, PlantsimDatatype):
    """Abstraction class for plantsim date datatype"""

    def to_plant(self):
        ...

    @staticmethod
    def from_plant(value) -> PlantsimDateTime:
        ...


class PlantsimJson(dict, PlantsimDatatype):
    """Abstraction class for plantsim json datatype"""

    def to_plant(self):
        ...

    @staticmethod
    def from_plant(value) -> PlantsimDateTime:
        ...


class PlantsimLength(float, PlantsimDatatype):
    """Abstraction class for plantsim length datatype"""

    def to_plant(self):
        ...

    @staticmethod
    def from_plant(value) -> PlantsimDateTime:
        ...


class PlantsimList(list, PlantsimDatatype):
    """Abstraction class for plantsim list datatype"""

    def to_plant(self):
        ...

    @staticmethod
    def from_plant(value) -> PlantsimDateTime:
        ...


class PlantsimListrange(list, PlantsimDatatype):
    """Abstraction class for plantsim listrange datatype"""

    def to_plant(self):
        ...

    @staticmethod
    def from_plant(value) -> PlantsimDateTime:
        ...


class PlantsimObject(dict, PlantsimDatatype):
    """Abstraction class for plantsim object datatype"""

    def to_plant(self):
        ...

    @staticmethod
    def from_plant(value) -> PlantsimDateTime:
        ...


class PlantsimQueue(list, PlantsimDatatype):
    """Abstraction class for plantsim queue datatype"""

    def to_plant(self):
        ...

    @staticmethod
    def from_plant(value) -> PlantsimDateTime:
        ...


class PlantsimReal(float, PlantsimDatatype):
    """Abstraction class for plantsim real datatype"""

    def to_plant(self):
        ...

    @staticmethod
    def from_plant(value) -> PlantsimDateTime:
        ...


class PlantsimSpeed(float, PlantsimDatatype):
    """Abstraction class for plantsim speed datatype"""

    def to_plant(self):
        ...

    @staticmethod
    def from_plant(value) -> PlantsimDateTime:
        ...


class PlantsimStack(list, PlantsimDatatype):
    """Abstraction class for plantsim stack datatype"""

    def to_plant(self):
        ...

    @staticmethod
    def from_plant(value) -> PlantsimDateTime:
        ...


class PlantsimString(str, PlantsimDatatype):
    """Abstraction class for plantsim string datatype"""

    def to_plant(self):
        ...

    @staticmethod
    def from_plant(value) -> PlantsimDateTime:
        ...


class PlantsimTable(dict, PlantsimDatatype):
    """Abstraction class for plantsim table datatype"""

    def to_plant(self):
        ...

    @staticmethod
    def from_plant(value) -> PlantsimDateTime:
        ...


class PlantsimWeight(float, PlantsimDatatype):
    """Abstraction class for plantsim weight datatype"""

    def to_plant(self):
        ...

    @staticmethod
    def from_plant(value) -> PlantsimDateTime:
        ...


enum_class_switch: Dict[PlantsimDatatype] = {
    PlantsimDatatypes.TIME: PlantsimTime
}
