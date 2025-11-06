from dataclasses import dataclass
from typing import List


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
class CallCycle:
    callers: List[CallerEntry]

    @staticmethod
    def from_dict(d: dict) -> "CallCycle":
        return CallCycle(
            callers=[CallerEntry.from_dict(c) for c in d.get("Callers", [])]
        )
