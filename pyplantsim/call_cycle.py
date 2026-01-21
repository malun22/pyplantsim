from dataclasses import dataclass
from typing import List


class MissingMethodError(ValueError):
    """Raised when the 'Method' key is missing or invalid in a CallCycle mapping."""


@dataclass
class CallerEntry:
    caller: str
    called: int
    self_time: float
    callees_time: float

    @staticmethod
    def from_dict(d: dict) -> "CallerEntry":
        return CallerEntry(
            caller=d["Caller"],
            called=d["Called"],
            self_time=d["SelfTime"],
            callees_time=d["CalleesTime"],
        )


@dataclass
class CallCycleMethod:
    method: str
    called: int
    self_: int
    self_time: float
    callees_time: float

    @staticmethod
    def from_dict(d: dict) -> "CallCycleMethod":
        return CallCycleMethod(
            method=d["Method"],
            called=d["Called"],
            self_=d["Self"],
            self_time=d["SelfTime"],
            callees_time=d["CalleesTime"],
        )


@dataclass
class CallCycle:
    method: CallCycleMethod
    callers: List[CallerEntry]

    @staticmethod
    def from_dict(d: dict) -> "CallCycle":
        if "Method" not in d:
            raise MissingMethodError("Key 'Method' is required in CallCycle dict")

        method_dict = d.get("Method")
        if not isinstance(method_dict, dict):
            raise MissingMethodError("'Method' must be a dict")

        return CallCycle(
            method=CallCycleMethod.from_dict(method_dict),
            callers=[CallerEntry.from_dict(c) for c in d.get("Callers", [])],
        )
