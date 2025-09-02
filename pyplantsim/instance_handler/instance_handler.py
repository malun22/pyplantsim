import queue
import threading

import time
import gc
import pythoncom
import psutil

from typing import Callable, Optional, Union, Dict, Unpack, TypedDict, List
from abc import ABC


from ..plantsim import Plantsim
from ..exception import SimulationException
from ..licenses import PlantsimLicense
from ..versions import PlantsimVersion
from .job import Job, SimulationJob, ShutdownWorkerJob
from .exception import InstanceHandlerNotInitializedException


class BaseInstanceHandlerKwargs(TypedDict, total=False):
    """
    Typed dictionary for keyword arguments passed to PlantSim instance handlers.

    :key version: PlantSim version to use.
    :type version: Union[PlantsimVersion, str]
    :key visible: Whether the PlantSim UI should be visible.
    :type visible: bool
    :key trusted: Whether the PlantSim instance should run in trusted mode.
    :type trusted: bool
    :key license: PlantSim license type.
    :type license: Union[PlantsimLicense, str]
    :key suppress_3d: Suppress 3D window.
    :type suppress_3d: bool
    :key show_msg_box: Show message box on errors.
    :type show_msg_box: bool
    :key event_polling_interval: Interval for event polling (seconds).
    :type event_polling_interval: float
    :key disable_log_message: Disable log messages.
    :type disable_log_message: bool
    :key simulation_finished_callback: Callback for finished simulation.
    :type simulation_finished_callback: Optional[Callable[[], None]]
    :key simtalk_msg_callback: Callback for SimTalk messages.
    :type simtalk_msg_callback: Optional[Callable[[str], None]]
    :key fire_simtalk_msg_callback: Callback for fired SimTalk messages.
    :type fire_simtalk_msg_callback: Optional[Callable[[str], None]]
    :key simulation_error_callback: Callback for simulation errors.
    :type simulation_error_callback: Optional[Callable[[SimulationException], None]]
    """

    version: Union[PlantsimVersion, str]
    visible: bool
    trusted: bool
    license: Union[PlantsimLicense, str]
    suppress_3d: bool
    show_msg_box: bool
    event_polling_interval: float
    disable_log_message: bool
    simulation_finished_callback: Optional[Callable[[], None]]
    simtalk_msg_callback: Optional[Callable[[str], None]]
    fire_simtalk_msg_callback: Optional[Callable[[str], None]]
    simulation_error_callback: Optional[Callable[[SimulationException], None]]


class BaseInstanceHandler(ABC):
    """
    Handles multiple pyplantsim workers, each with its own Plantsim instance.

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
        self._job_queue: queue.Queue[Job] = queue.Queue()
        self._shutdown_event = threading.Event()
        self._workers = []
        self._workers_lock = threading.Lock()
        self._results: Dict[str, threading.Event] = {}
        self._cancel_flags: Dict[str, threading.Event] = {}

        self._plantsim_kwargs = dict(
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

        self._initialized = False

    def __enter__(self) -> "BaseInstanceHandler":
        """
        Enter the runtime context related to this object.

        :returns: InstanceHandler object
        :rtype: InstanceHandler
        """
        return self.initialize()

    def __exit__(self, _, __, ___):
        """
        Exit the runtime context and shut down all workers.
        """
        self.shutdown()

    def initialize(self) -> "BaseInstanceHandler":
        self._initialized = True

    def requires_initialized(method):
        def wrapper(self, *args, **kwargs):
            if not self._initialized:
                raise InstanceHandlerNotInitializedException("initialize() not called")
            return method(self, *args, **kwargs)

        return wrapper

    @requires_initialized
    def _create_worker(
        self, **plantsim_kwargs: Unpack[BaseInstanceHandlerKwargs]
    ) -> None:
        """
        Create a new worker and add it to the worker list.

        :param plantsim_kwargs: Keyword arguments for the Plantsim instance.
        :type plantsim_kwargs: BaseInstanceHandlerKwargs
        """
        with self._workers_lock:
            t = threading.Thread(
                target=self._worker, args=(plantsim_kwargs,), daemon=True
            )
            t.start()
            self._workers.append(t)

    @requires_initialized
    def shutdown(self) -> None:
        """
        Shut down all workers and wait until all jobs are finished.
        """
        self._shutdown_event.set()
        self._job_queue.join()

        num_workers = self.number_instances
        jobs: List[ShutdownWorkerJob] = []
        for _ in range(num_workers):
            jobs.append(self._shotdown_next_worker())

        for job in jobs:
            self.wait_for(job)

        with self._workers_lock:
            workers = list(self._workers)

        for t in workers:
            t.join()

        self._initialized = False

    @requires_initialized
    def _shotdown_next_worker(self) -> ShutdownWorkerJob:
        """
        Shuts down the next available worker by queueing a ShutdownWorkerJob
        """
        job = ShutdownWorkerJob()
        self.queue_job(job)
        return job

    @requires_initialized
    def _worker(self, plantsim_args) -> None:
        """
        Worker thread that processes simulation jobs.

        :param plantsim_args: Arguments for the Plantsim instance.
        """
        pythoncom.CoInitialize()

        try:
            with Plantsim(**plantsim_args) as instance:
                while True:
                    job = self._job_queue.get()

                    if isinstance(job, ShutdownWorkerJob):
                        self._finish_job(job)
                        break
                    elif not isinstance(job, SimulationJob):
                        self._finish_job(job)
                        raise TypeError(f"Unexpected job type: {type(job)}")

                    cancel_event = self._cancel_flags.get(job.job_id)

                    try:
                        instance.run_simulation(
                            without_animation=job.without_animation,
                            on_progress=job.on_progress,
                            on_endsim=job.on_endsim,
                            on_init=job.on_init,
                            on_simulation_error=job.on_simulation_error,
                            cancel_event=cancel_event,
                        )
                    finally:
                        self._finish_job(job)
        finally:
            time.sleep(0.1)
            pythoncom.CoUninitialize()
            gc.collect()

    @requires_initialized
    def _finish_job(self, job: Job) -> None:
        """
        Mark a job as finished and signal waiting events.

        :param job: The job object to finish.
        :type job: Job
        """
        finished_event = self._results.get(job.job_id)
        if finished_event:
            finished_event.set()
        self._job_queue.task_done()

    @requires_initialized
    def queue_job(self, job: Job) -> Job:
        """
        Add a job to the queue for processing.

        :param job: The job to queue.
        :type job: Job
        :returns: The queued job.
        :rtype: Job
        """
        finished_event = threading.Event()
        self._results[job.job_id] = finished_event

        cancel_event = threading.Event()
        self._cancel_flags[job.job_id] = cancel_event

        self._job_queue.put(job)
        return job

    @requires_initialized
    def wait_for(self, job: Job):
        """
        Block until the the given job is finished.

        :param job: The job object to wait for.
        :type job: Job
        :raises ValueError: If the job ID does not exist.
        """
        event = self._results.get(job.job_id)
        if event is not None:
            event.wait()
        else:
            raise ValueError(f"No such job id: {job.job_id}")

    @requires_initialized
    def wait_all(self) -> None:
        """
        Block until all queued jobs are finished.
        """
        self._job_queue.join()

    @requires_initialized
    def empty_queue(self) -> None:
        """
        Remove all not-yet-started jobs from the queue.
        """
        with self._job_queue.mutex:
            self._job_queue.queue.clear()

    @requires_initialized
    def remove_queued_job(self, job: Job) -> bool:
        """
        Remove a specific job from the queue by its job_id.

        :param job: The job to remove.
        :type job: Job
        :returns: True if the job was found and removed, False otherwise.
        :rtype: bool
        """
        removed = False
        with self._job_queue.mutex:
            new_queue = queue.deque()
            while self._job_queue.queue:
                queued_job = self._job_queue.queue.popleft()
                if queued_job is not None and queued_job.job_id == job.job_id:
                    removed = True
                    self._results.pop(job.job_id, None)
                else:
                    new_queue.append(queued_job)
            self._job_queue.queue = new_queue
        return removed

    @requires_initialized
    def cancel_running_job(self, job: Job) -> bool:
        """
        Signal all running jobs to cancel.

        :returns: The number of jobs that were signaled for cancellation.
        :rtype: int
        """
        cancel_event = self._cancel_flags.get(job.job_id)
        if cancel_event:
            cancel_event.set()
            return True
        return False

    @requires_initialized
    def cancel_running_jobs(self) -> int:
        """
        Signal all running jobs to cancel.

        :return: The number of jobs that were signaled for cancellation.
        """
        count = 0
        for cancel_event in self._cancel_flags.values():
            if cancel_event is not None and not cancel_event.is_set():
                cancel_event.set()
                count += 1
        return count

    @property
    def number_instances(self) -> int:
        """
        Get the number of PlantSim instances managed.

        :return: Number of instances.
        :rtype: int
        """
        with self._workers_lock:
            return len(self._workers)


class FixedInstanceHandler(BaseInstanceHandler):
    """
    Handles a fixed amount of Plantsim instances.

    :param amount_instances: Number of PlantSim instances to create.
    :type amount_instances: int
    :param kwargs: Additional keyword arguments for PlantSim instances.
    :type kwargs: BaseInstanceHandlerKwargs
    """

    _amount_instances: int

    def __init__(
        self, amount_instances: int, **kwargs: Unpack[BaseInstanceHandlerKwargs]
    ):
        """
        Initialize the FixedInstanceHandler.

        :param amount_instances: Number of PlantSim instances to create.
        :type amount_instances: int
        :param kwargs: Additional keyword arguments for PlantSim instances.
        :type kwargs: BaseInstanceHandlerKwargs
        """
        super().__init__(**kwargs)
        self._amount_instances = amount_instances

    def initialize(self) -> "FixedInstanceHandler":
        super().initialize()
        self._create_workers(self._amount_instances)
        return self

    def _create_workers(self, amount_workers: int) -> None:
        """
        Create worker threads for simulation.

        :param amount_workers: Number of workers to create.
        :type amount_workers: int
        :param plantsim_kwargs: Keyword arguments for Plantsim instances.
        """
        for _ in range(amount_workers):
            self._create_worker(**self._plantsim_kwargs)


class DynamicInstanceHandler(BaseInstanceHandler):
    """
    Dynamically manages the number of PlantSim worker instances based on system resource usage.

    This handler automatically scales the amount of worker instances up or down depending
    on CPU and memory usage. It ensures that at least ``min_instances`` and at most
    ``max_instances`` workers are active. Resource checks and scaling occur at a fixed interval.

    :param max_cpu: Maximum allowed CPU usage (fraction, e.g., 0.8 for 80%).
    :type max_cpu: float
    :param max_memory: Maximum allowed memory usage (fraction, e.g., 0.8 for 80%).
    :type max_memory: float
    :param min_instances: Minimum number of PlantSim worker instances.
    :type min_instances: int
    :param max_instances: Maximum number of PlantSim worker instances.
    :type max_instances: Optional[int]
    :param scale_interval: Seconds between resource checks and scaling decisions.
    :type scale_interval: float
    :param kwargs: Additional keyword arguments forwarded to the PlantSim instance.
    :type kwargs: BaseInstanceHandlerKwargs
    """

    def __init__(
        self,
        max_cpu: float = 0.8,
        max_memory: float = 0.8,
        min_instances: int = 1,
        max_instances: Optional[int] = None,
        scale_interval: float = 15.0,
        **kwargs: Unpack[BaseInstanceHandlerKwargs],
    ):
        """
        Initialize the dynamic handler and start the scaler thread.

        :param max_cpu: Maximum allowed CPU usage (fraction, e.g., 0.8 for 80%).
        :param max_memory: Maximum allowed memory usage (fraction, e.g., 0.8 for 80%).
        :param min_instances: Minimum number of worker instances.
        :param max_instances: Maximum number of worker instances.
        :param scale_interval: Seconds between scale checks.
        :param kwargs: Additional keyword arguments for PlantSim instances.
        """
        super().__init__(**kwargs)
        self.max_cpu = max_cpu
        self.max_memory = max_memory
        self.min_instances = min_instances
        self.max_instances = max_instances
        self.scale_interval = scale_interval

    def initialize(self) -> "DynamicInstanceHandler":
        super().initialize()

        self._active = True

        for _ in range(self.min_instances):
            self._create_worker(**self._plantsim_kwargs)

        self._scaler_thread = threading.Thread(target=self._scaler, daemon=True)
        self._scaler_thread.start()

        return self

    def _scaler(self):
        """
        Background thread that monitors system resources and dynamically scales
        the number of PlantSim worker instances.

        The scaler checks CPU and memory usage at regular intervals and
        increases or decreases the number of workers accordingly.
        """
        psutil.cpu_percent()
        time.sleep(self.scale_interval)
        while self._active:
            cpu = psutil.cpu_percent(interval=1) / 100.0
            mem = psutil.virtual_memory().percent / 100.0
            current_instances = self.number_instances

            if not self._active:
                break

            if (
                (cpu < self.max_cpu)
                and (mem < self.max_memory)
                and (
                    self.max_instances is None
                    or (current_instances < self.max_instances)
                )
                and not self._job_queue.empty()
            ):
                self._create_worker(**self._plantsim_kwargs)
            elif (current_instances > self.min_instances) and (
                cpu > self.max_cpu or mem > self.max_memory
            ):
                job = self._shotdown_next_worker()
                self.wait_for(
                    job
                )  # Wait for the worker to shut down before continuing the scaling process

            if not self._active:
                break

            time.sleep(self.scale_interval)

    def shutdown(self):
        """
        Shut down the dynamic handler and all managed worker threads.

        This method signals the scaler thread to stop, shuts down all workers,
        and waits for the scaler thread to terminate.
        """
        self._active = False
        super().shutdown()
        if self._scaler_thread.is_alive():
            self._scaler_thread.join()
