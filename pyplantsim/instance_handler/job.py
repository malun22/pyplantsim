from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from dataclasses import field
from typing import Callable
import uuid

from ..exception import SimulationException
from ..plantsim import Plantsim


@dataclass
class Job(ABC):
    """
    Abstract base class representing a job to be handled by a worker.

    :ivar job_id: Unique identifier for the job.
    :vartype job_id: str
    """

    job_id: str = field(init=False)

    def __post_init__(self) -> None:
        """
        Initialize the job with a unique UUID as its job_id.
        """
        self.job_id = str(uuid.uuid4())


@dataclass
class SimulationJob(Job):
    """
    Represents a simulation job to be processed by a PlantSim worker.

    :ivar without_animation: If True, run the simulation without animation.
    :vartype without_animation: bool
    :ivar on_init: Callback to be called at simulation initialization.
    :vartype on_init: Callable[[Plantsim], None] | None = None
    :ivar on_endsim: Callback to be called at simulation end.
    :vartype on_endsim: Callable[[Plantsim], None] | None = None
    :ivar on_simulation_error: Callback to be called on simulation error.
    :vartype on_simulation_error: Callable[[Plantsim, SimulationException], None] | None = None
    :ivar on_progress: Callback to be called to report progress.
    :vartype on_progress: Callable[[Plantsim, float], None] | None = None
    """

    without_animation: bool = True
    on_init: Callable[[Plantsim], None] | None = None
    on_endsim: Callable[[Plantsim], None] | None = None
    on_simulation_error: Callable[[Plantsim, SimulationException], None] | None = None
    on_progress: Callable[[Plantsim, float], None] | None = None


class ShutdownWorkerJob(Job):
    """
    Special job class used to signal a worker to shut down.

    Inherits from :class:`Job`.
    """

    ...
