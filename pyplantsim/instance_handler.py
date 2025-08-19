import queue
import threading
from typing import Callable, Optional, Union

from .exception import SimulationException
from .licenses import PlantsimLicense
from .versions import PlantsimVersion


class InstanceHandler:
    """
    Handles multiple pyplantsim workers, each with its own Plantsim instance.

    :param amount_instances: Number of PlantSim instances to create.
    :type amount_instances: int
    :param version: PlantSim version to use.
    :type version: Union[PlantsimVersion, str]
    :param visible: Whether the PlantSim UI should be visible.
    :type visible: bool
    :param trusted: Whether the PlantSim instance should run in trusted mode.
    :type trusted: bool
    :param license: PlantSim license type.
    :type license: Union[PlantsimLicense, str]
    :param suppress_3d: Suppress 3D window.
    :type suppress_3d: bool
    :param show_msg_box: Show message box on errors.
    :type show_msg_box: bool
    :param event_polling_interval: Interval for event polling.
    :type event_polling_interval: float
    :param disable_log_message: Disable log messages.
    :type disable_log_message: bool
    :param simulation_finished_callback: Callback for finished simulation.
    :type simulation_finished_callback: Optional[Callable[[], None]]
    :param simtalk_msg_callback: Callback for SimTalk messages.
    :type simtalk_msg_callback: Optional[Callable[[str], None]]
    :param fire_simtalk_msg_callback: Callback for fired SimTalk messages.
    :type fire_simtalk_msg_callback: Optional[Callable[[str], None]]
    :param simulation_error_callback: Callback for simulation errors.
    :type simulation_error_callback: Optional[Callable[[SimulationException], None]]
    """

    def __init__(
        self,
        amount_instances: int,
        version: Union[PlantsimVersion, str] = PlantsimVersion.V_MJ_22_MI_1,
        visible: bool = False,
        trusted: bool = False,
        license: Union[PlantsimLicense, str] = PlantsimLicense.VIEWER,
        suppress_3d: bool = False,
        show_msg_box: bool = False,
        event_polling_interval: float = 0.05,
        disable_log_message: bool = False,
        simulation_finished_callback: Optional[Callable[[], None]] = None,
        simtalk_msg_callback: Optional[Callable[[str], None]] = None,
        fire_simtalk_msg_callback: Optional[Callable[[str], None]] = None,
        simulation_error_callback: Optional[
            Callable[[SimulationException], None]
        ] = None,
    ):
        """
        Initialize the InstanceHandler with the given parameters.
        """
        self._job_queue = queue.Queue()
        self._shutdown_event = threading.Event()
        self._workers = []
        self._num_workers = 0

        plantsim_kwargs = dict(
            version=version,
            visible=visible,
            trusted=trusted,
            license=license,
            suppress_3d=suppress_3d,
            show_msg_box=show_msg_box,
            event_polling_interval=event_polling_interval,
            disable_log_message=disable_log_message,
            simulation_finished_callback=simulation_finished_callback,
            simtalk_msg_callback=simtalk_msg_callback,
            fire_simtalk_msg_callback=fire_simtalk_msg_callback,
            simulation_error_callback=simulation_error_callback,
        )

        self._create_workers(amount_instances, **plantsim_kwargs)

    def __enter__(self):
        """
        Enter the runtime context related to this object.

        :return: InstanceHandler object
        :rtype: InstanceHandler
        """
        return self

    def __exit__(self, _, __, ___):
        """
        Exit the runtime context and shut down all workers.
        """
        self.shutdown()

    def _create_workers(self, amount_workers: int, **plantsim_kwargs):
        """
        Create worker threads for simulation.

        :param amount_workers: Number of workers to create.
        :type amount_workers: int
        :param plantsim_kwargs: Keyword arguments for Plantsim instances.
        """
        self._num_workers = amount_workers
        for _ in range(amount_workers):
            t = threading.Thread(
                target=self._worker, args=(plantsim_kwargs,), daemon=True
            )
            t.start()
            self._workers.append(t)

    def shutdown(self):
        """
        Shut down all workers and wait until all jobs are finished.
        """
        self._shutdown_event.set()
        self._job_queue.join()

        for _ in range(self._num_workers):
            self._job_queue.put(None)

        for t in self._workers:
            t.join()

    def _worker(self, plantsim_args):
        """
        Worker thread that processes simulation jobs.

        :param plantsim_args: Arguments for the Plantsim instance.
        """
        import pythoncom

        pythoncom.CoInitialize()
        from .plantsim import Plantsim

        with Plantsim(**plantsim_args) as instance:
            while True:
                job = self._job_queue.get()
                if job is None:
                    # Stop-Signal
                    self._job_queue.task_done()
                    break
                (
                    without_animation,
                    on_init,
                    on_endsim,
                    on_simulation_error,
                    on_progress,
                ) = job
                try:
                    instance.run_simulation(
                        without_animation=without_animation,
                        on_progress=on_progress,
                        on_endsim=on_endsim,
                        on_init=on_init,
                        on_simulation_error=on_simulation_error,
                    )
                finally:
                    self._job_queue.task_done()

    def run_simulation(
        self,
        without_animation: bool = True,
        on_init: Optional[Callable] = None,
        on_endsim: Optional[Callable] = None,
        on_simulation_error: Optional[Callable] = None,
        on_progress: Optional[Callable] = None,
    ) -> None:
        """
        Queue a simulation to be run by an available worker.

        :param without_animation: Whether the simulation should be run without animation.
        :type without_animation: bool
        :param on_init: Initialization callback.
        :type on_init: Optional[Callable]
        :param on_endsim: Simulation end callback.
        :type on_endsim: Optional[Callable]
        :param on_simulation_error: Simulation error callback.
        :type on_simulation_error: Optional[Callable]
        :param on_progress: Progress callback.
        :type on_progress: Optional[Callable]
        """
        self._job_queue.put(
            (without_animation, on_init, on_endsim, on_simulation_error, on_progress)
        )

    def wait_all(self):
        """
        Block until all queued simulation jobs are finished.
        """
        self._job_queue.join()

    @property
    def number_instances(self) -> int:
        """
        Get the number of PlantSim instances managed.

        :return: Number of instances.
        :rtype: int
        """
        return self._num_workers
