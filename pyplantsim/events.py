from typing import Callable, Optional


class PlantSimEvents:
    on_simulation_finished: Optional[Callable[[], None]]
    on_simtalk_message: Optional[Callable[[str], None]]
    on_fire_simtalk_message: Optional[Callable[[str], None]]

    def __init__(
        self,
        on_simulation_finished: Optional[Callable[[], None]] = None,
        on_simtalk_message: Optional[Callable[[str], None]] = None,
        on_fire_simtalk_message: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.on_simulation_finished = on_simulation_finished
        self.on_simtalk_message = on_simtalk_message
        self.on_fire_simtalk_message = on_fire_simtalk_message

    def OnSimulationFinished(self):
        if self.on_simulation_finished:
            self.on_simulation_finished()

    def OnSimTalkMessage(self, msg: str):
        if self.on_simtalk_message:
            self.on_simtalk_message(msg)

    def FireSimTalkMessage(self, msg: str):
        if self.on_fire_simtalk_message:
            self.on_fire_simtalk_message(msg)
