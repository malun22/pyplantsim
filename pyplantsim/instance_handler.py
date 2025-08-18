import threading
import queue
from typing import Callable, Optional
from .licenses import PlantsimLicense
from .versions import PlantsimVersion
from .exception import SimulationException


class InstanceHandler:
    """
    Handles multiple pyplantsim workers, each with its own Plantsim instance.
    """

    def __init__(self):
        self._job_queue = queue.Queue()
        self._shutdown_event = threading.Event()
        self._workers = []
        self._num_workers = 0

    def __enter__(self):
        return self

    def __exit__(self, _, __, ___):
        self.shutdown()

    def create_workers(
        self,
        amount_workers: int,
        version=PlantsimVersion.V_MJ_25_MI_4,
        visible: bool = True,
        trusted: bool = True,
        license: PlantsimLicense = PlantsimLicense.STUDENT,
        suppress_3d: bool = False,
        show_msg_box: bool = False,
    ):
        self._num_workers = amount_workers
        plantsim_args = dict(
            version=version,
            visible=visible,
            trusted=trusted,
            license=license,
            suppress_3d=suppress_3d,
            show_msg_box=show_msg_box,
        )
        for _ in range(amount_workers):
            t = threading.Thread(
                target=self._worker, args=(plantsim_args,), daemon=True
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

        instance = Plantsim(**plantsim_args)
        while True:
            job = self._job_queue.get()
            if job is None:
                # Stop-Signal
                self._job_queue.task_done()
                break
            without_animation, on_init, on_endsim, on_simulation_error = job
            try:
                if on_init:
                    on_init(instance)
                try:
                    instance.run_simulation(without_animation=without_animation)
                    if on_endsim:
                        on_endsim(instance)
                except SimulationException as ex:
                    if on_simulation_error:
                        on_simulation_error(instance, ex)
            finally:
                self._job_queue.task_done()
        instance.quit()

    def run_simulation(
        self,
        without_animation: bool = True,
        on_init: Optional[Callable] = None,
        on_endsim: Optional[Callable] = None,
        on_simulation_error: Optional[Callable] = None,
    ) -> None:
        self._job_queue.put(
            (without_animation, on_init, on_endsim, on_simulation_error)
        )

    def wait_all(self):
        self._job_queue.join()
