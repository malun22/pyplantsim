import queue
import threading
from typing import Callable, Optional, Union

from .exception import SimulationException
from .licenses import PlantsimLicense
from .versions import PlantsimVersion


class InstanceHandler:
    """
    Handles multiple pyplantsim workers, each with its own Plantsim instance.
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
        return self

    def __exit__(self, _, __, ___):
        self.shutdown()

    def _create_workers(self, amount_workers: int, **plantsim_kwargs):
        self._num_workers = amount_workers
        for _ in range(amount_workers):
            t = threading.Thread(
                target=self._worker, args=(plantsim_kwargs,), daemon=True
            )
            t.start()
            self._workers.append(t)

    def shutdown(self):
        self._shutdown_event.set()
        self._job_queue.join()

        for _ in range(self._num_workers):
            self._job_queue.put(None)

        for t in self._workers:
            t.join()

    def _worker(self, plantsim_args):
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
        self._job_queue.put(
            (without_animation, on_init, on_endsim, on_simulation_error, on_progress)
        )

    def wait_all(self):
        self._job_queue.join()

    @property
    def number_instances(self) -> int:
        return self._num_workers
