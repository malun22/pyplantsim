from dataclasses import dataclass
from .plantsim import Plantsim
from plantsimpath import PlantsimPath
from typing import Optional


@dataclass
class EventController:
    _instance: Plantsim
    _path: PlantsimPath
    _error_handler: Optional[PlantsimPath] = None

    def __init__(
        self,
        instance: Plantsim,
        path: PlantsimPath,
        install_error_handler: bool = False,
    ):
        self._instance = instance
        self._path = path

        if install_error_handler:
            self.install_error_handler()

    def install_error_handler(self):
        """
        Install an error handler in the model file under basis.ErrorHandler. Searches for any method object and duplicates that.

        :raises Exception: If error handler could not be created.
        """
        simtalk = self._load_simtalk_script("install_error_handler")

        response = self.execute_sim_talk(simtalk)

        if not response:
            self._error_handler = None
            raise Exception("Could not create Error Handler")

        self._error_handler = PlantsimPath("basis", "ErrorHandler")

    def reset_simulation(self) -> None:
        """
        Reset the simulation.

        :raises Exception: If EventController is not set.
        """
        self._simulation_error = None
        self._instance.ResetSimulation(str(self._path))
