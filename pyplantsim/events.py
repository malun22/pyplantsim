from typing import Callable, Optional


class PlantSimEvents:
    """
    Event handler class for Plant Simulation COM events.

    :param on_simulation_finished: Callback for when the simulation is finished.
    :type on_simulation_finished: Optional[Callable[[], None]]
    :param on_simtalk_message: Callback for when a SimTalk message is received.
    :type on_simtalk_message: Optional[Callable[[str], None]]
    :param on_fire_simtalk_message: Callback for when a SimTalk message is fired.
    :type on_fire_simtalk_message: Optional[Callable[[str], None]]

    :ivar on_simulation_finished: Callback for simulation finished event.
    :vartype on_simulation_finished: Optional[Callable[[], None]]
    :ivar on_simtalk_message: Callback for SimTalk message event.
    :vartype on_simtalk_message: Optional[Callable[[str], None]]
    :ivar on_fire_simtalk_message: Callback for fired SimTalk message event.
    :vartype on_fire_simtalk_message: Optional[Callable[[str], None]]
    """

    on_simulation_finished: Optional[Callable[[], None]]
    on_simtalk_message: Optional[Callable[[str], None]]
    on_fire_simtalk_message: Optional[Callable[[str], None]]

    def __init__(
        self,
        on_simulation_finished: Optional[Callable[[], None]] = None,
        on_simtalk_message: Optional[Callable[[str], None]] = None,
        on_fire_simtalk_message: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Initialize the PlantSimEvents event handler.

        :param on_simulation_finished: Callback for simulation finished event.
        :type on_simulation_finished: Optional[Callable[[], None]]
        :param on_simtalk_message: Callback for SimTalk message event.
        :type on_simtalk_message: Optional[Callable[[str], None]]
        :param on_fire_simtalk_message: Callback for fired SimTalk message event.
        :type on_fire_simtalk_message: Optional[Callable[[str], None]]
        """
        self.on_simulation_finished = on_simulation_finished
        self.on_simtalk_message = on_simtalk_message
        self.on_fire_simtalk_message = on_fire_simtalk_message

    def OnSimulationFinished(self):
        """
        Triggered when the simulation is finished. Calls the registered callback if available.
        """
        if self.on_simulation_finished:
            self.on_simulation_finished()

    def OnSimTalkMessage(self, msg: str):
        """
        Triggered when a SimTalk message is received. Calls the registered callback if available.

        :param msg: The SimTalk message.
        :type msg: str
        """
        if self.on_simtalk_message:
            self.on_simtalk_message(msg)

    def FireSimTalkMessage(self, msg: str):
        """
        Triggered when a SimTalk message is fired. Calls the registered callback if available.

        :param msg: The SimTalk message.
        :type msg: str
        """
        if self.on_fire_simtalk_message:
            self.on_fire_simtalk_message(msg)
