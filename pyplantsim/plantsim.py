import os
import threading
import win32com.client
import pythoncom
import time
import json
import pandas as pd
import importlib.resources
from packaging.version import Version

from pathlib import Path
from typing import Union, Any, Optional, List, Callable
from loguru import logger
from datetime import datetime, timedelta

from .versions import PlantsimVersion
from .licenses import PlantsimLicense
from .exception import PlantsimException, SimulationException
from .path import PlantsimPath
from .events import PlantSimEvents


class Plantsim:
    """
    Wrapper class for the Siemens Tecnomatix Plant Simulation COM interface.

    Attributes:
    ----------
    _dispatch_id : str
        COM dispatch identifier for the RemoteControl interface.
    _event_controller : PlantsimPath
        Path to the event controller.
    _version : PlantsimVersion or str
        Plant Simulation version to be used.
    _visible : bool
        Whether the instance window is visible.
    _trusted : bool
        Whether the instance has access to the computer.
    _license : PlantsimLicense or str
        License to be used.
    _suppress_3d : bool
        Suppresses the start of the 3D view.
    _show_msg_box : bool
        Whether to show a message box.
    _network_path : str
        Network path.
    _event_thread
        Event thread object.
    _event_handler : PlantSimEvents
        Handler for Plant Simulation events.
    _event_polling_interval : float
        Interval for polling events.
    _datetime_format : str
        Format for datetime strings
    _model_loaded : bool
        Whether a model has been loaded.
    _model_path : str
        Path to the loaded model.
    _running : str
        Simulation status.
    _simulation_error : Optional[dict]
        Simulation error details.
    _simulation_finished_event : threading.Event
        Event triggered when the simulation finishes.
    _error_handler : Optional[str]
        The path to the installed error handler
    _user_simulation_finished_cb : Optional[Callable[[], None]]
        Callback for when the simulation finishes.
    _user_simtalk_msg_cb : Optional[Callable[[str], None]]
        Callback for SimTalk messages.
    _user_fire_simtalk_msg_cb : Optional[Callable[[str], None]]
        Callback to fire SimTalk messages.
    _user_simulation_error_cb : Optional[Callable[[SimulationException], None]]
        Callback for simulation errors.
    """

    # Defaults
    _dispatch_id: str = "Tecnomatix.PlantSimulation.RemoteControl"
    _event_controller: PlantsimPath = None
    _version: Version = None
    _visible: bool = None
    _trusted: bool = None
    _license: Union[PlantsimLicense, str] = None
    _suppress_3d: bool = None
    _show_msg_box: bool = None
    _network_path: str = None
    _event_thread = None
    _event_handler: PlantSimEvents = None
    _event_polling_interval: float = 0.05
    _datetime_format: str

    # State management
    _model_loaded: bool = False
    _model_path: str = None
    _running: str = False
    _simulation_error: Optional[dict] = None
    _simulation_finished_event: threading.Event = None
    _error_handler: Optional[str] = None

    # Callbacks
    _user_simulation_finished_cb: Optional[Callable[[], None]] = None
    _user_simtalk_msg_cb: Optional[Callable[[str], None]] = None
    _user_fire_simtalk_msg_cb: Optional[Callable[[str], None]] = None
    _user_simulation_error_cb: Optional[Callable[[SimulationException], None]] = None

    def __init__(
        self,
        version: Union[PlantsimVersion, str] = PlantsimVersion.V_MJ_22_MI_1,
        visible: bool = True,
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
    ) -> None:
        """
        Initializes the Siemens Tecnomatix Plant Simulation instance.

        Parameters:
        ----------
        version : PlantsimVersion or str, optional
            Plant Simulation version to use (default: PlantsimVersion.V_MJ_22_MI_1).
        visible : bool, optional
            Whether the instance window is visible (default: True).
        trusted : bool, optional
            Whether the instance should have access to the computer (default: True).
        license : PlantsimLicense or str, optional
            License to use (default: PlantsimLicense.VIEWER).
        suppress_3d : bool, optional
            Suppress the start of 3D view (default: False).
        show_msg_box : bool, optional
            Show a message box (default: False).
        simulation_finished_callback : Callable[[], None], optional
            Callback function when simulation finishes.
        simtalk_msg_callback : Callable[[str], None], optional
            Callback for received SimTalk messages.
        fire_simtalk_msg_callback : Callable[[str], None], optional
            Callback to trigger SimTalk messages.
        simulation_error_callback : Callable[[SimulationException], None], optional
            Callback for simulation errors.
        event_polling_interval : float, optional
            Interval (in seconds) for polling events (default: 0.05).
        disable_log_message : bool, optional
            Disable log messages (default: False).
        """

        # Inits
        if disable_log_message:
            logger.disable(__name__)

        self.set_version(version)
        self._visible = visible
        self._trusted = trusted
        self._license = license
        self._suppress_3d = suppress_3d
        self._show_msg_box = show_msg_box
        self._event_polling_interval = event_polling_interval
        self._simulation_finished_event = threading.Event()
        self._simulation_error_event = threading.Event()

        self.register_on_simulation_finished(simulation_finished_callback)
        self.register_on_simtalk_message(simtalk_msg_callback)
        self.register_on_fire_simtalk_message(fire_simtalk_msg_callback)
        self.register_on_simulation_error(simulation_error_callback)

        self.start()

    def set_version(self, version: Union[PlantsimVersion, str]):
        self._version = Version(
            version.value if isinstance(version, PlantsimVersion) else version
        )

    def __enter__(self) -> "Plantsim":
        return self

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"version={self._version!r}, "
            f"visible={self._visible!r}, "
            f"trusted={self._trusted!r}, "
            f"license={self._license!r}, "
            f"suppress_3d={self._suppress_3d!r}, "
            f"show_msg_box={self._show_msg_box!r}, "
        )

    def start(self) -> "Plantsim":
        if self._running:
            raise Exception("Plant Simulation already running.")

        logger.info(
            f"Starting Siemens Tecnomatix Plant Simulation {str(self._version)} instance."
        )

        # Changing dispatch_id regarding requested version
        if self._version:
            self._dispatch_id += f".{str(self._version)}"

        # Initialize the Event Handler
        pythoncom.CoInitialize()
        self._event_handler = PlantSimEvents(
            on_simulation_finished=self._internal_simulation_finished,
            on_simtalk_message=self._user_simtalk_msg_cb,
            on_fire_simtalk_message=self._user_fire_simtalk_msg_cb,
        )

        # Dispatch the Instance
        try:
            self._instance = win32com.client.DispatchWithEvents(
                self._dispatch_id, type(self._event_handler)
            )
            self._running = True
        except Exception as e:
            raise PlantsimException(e)

        self._instance.on_simulation_finished = self._internal_simulation_finished
        self._instance.on_simtalk_message = self._internal_on_simtalk_message
        self._instance.on_fire_simtalk_message = self._user_fire_simtalk_msg_cb

        # Initialize Event Listening
        self._start_event_thread()

        # Set license
        try:
            self.set_license(self._license, force=True)
        except Exception as e:
            self.quit()
            raise PlantsimException(e)

        # Should the instance window be visible on screen
        self.set_visible(self._visible, force=True)

        # Should the instance have access to the computer or not
        self.set_trust_models(self._trusted, force=True)

        # Should the instance suppress the start of 3D
        self.set_suppress_start_of_3d(self._suppress_3d, force=True)

        # Should the instance show a message box
        self.set_show_message_box(self._show_msg_box, force=True)

        return self

    def __exit__(self, _, __, ___) -> None:
        self.stop()

    def stop(self) -> None:
        self._running = False
        self._close_event_thread()

        if self._instance:
            self.quit()

        pythoncom.CoUninitialize()

    def set_network(
        self,
        path: PlantsimPath,
        set_event_controller: bool = False,
        install_error_handler: bool = False,
    ) -> None:
        """Set the active network."""
        self._network_path = path
        self._instance.SetPathContext(str(self._network_path))

        if install_error_handler:
            self.install_error_handler()

        if set_event_controller:
            self.set_event_controller()

    def set_show_message_box(self, show: bool, force=False) -> None:
        """Should the instance show a message box"""
        if self._show_msg_box != show or force:
            self._show_msg_box = show
            self._instance.SetNoMessageBox(self._show_msg_box)

    def set_suppress_start_of_3d(self, suppress: bool, force=False) -> None:
        """Should the instance suppress the start of 3D"""
        if self._suppress_3d != suppress or force:
            self._suppress_3d = suppress
            self._instance.SetSuppressStartOf3D(self._suppress_3d)

    def set_license(self, license: PlantsimLicense, force=False) -> None:
        """Sets the license for the instance"""
        if self._license != license or force:
            self._license = license

            self._instance.SetLicenseType(
                self._license.value
                if isinstance(self._license, PlantsimLicense)
                else self._license
            )

    def set_visible(self, visible: bool, force=False) -> None:
        """Should the instance window be visible on screen"""
        if self._visible != visible or force:
            self._visible = visible
            self._instance.SetVisible(self._visible)

    def set_trust_models(self, trusted: bool, force=False) -> None:
        """Should the instance have access to the computer or not"""
        if self._trusted != trusted or force:
            self._trusted = trusted
            self._instance.SetTrustModels(self._trusted)

    def _start_event_thread(self):
        """Starts the event thread to listen to COM Events."""
        self._event_thread = threading.Thread(target=self._event_loop, daemon=True)
        self._event_thread.start()

    def _internal_simulation_finished(self):
        """Gets called when the simulation finishes."""
        self._simulation_finished_event.set()
        if self._user_simulation_finished_cb:
            self._user_simulation_finished_cb()

    def register_on_simulation_finished(self, callback: Optional[Callable[[], None]]):
        """Set Callback for OnSimulationFinished Event."""
        self._user_simulation_finished_cb = callback

    def _internal_on_simtalk_message(self, msg: str):
        """Gets called when the model sends a SimTalk message."""
        if self._is_json(msg):
            self._handle_simtalk_message(msg)

        if self._user_simtalk_msg_cb:
            self._user_simtalk_msg_cb(msg)

    def _handle_simtalk_message(self, msg: str):
        payload = json.loads(msg)

        if payload["status"] == "error":
            exception = SimulationException(
                payload["error"]["method_path"], payload["error"]["line_number"]
            )
            self._simulation_error_event.error = exception
            self._simulation_error_event.set()

            if self._user_simulation_error_cb:
                self._user_simulation_error_cb(exception)
        else:
            if self._user_simtalk_msg_cb:
                self._user_simtalk_msg_cb(msg)

    def _is_json(self, msg: str):
        try:
            json.loads(msg)
        except ValueError:
            return False
        return True

    def register_on_simtalk_message(self, callback: Optional[Callable[[str], None]]):
        """Set Callback for OnSimTalkMessage Event."""
        self._user_simtalk_msg_cb = callback

    def register_on_fire_simtalk_message(
        self, callback: Optional[Callable[[str], None]]
    ):
        """Set Callback for FireSimTalkMessage Event."""
        self._user_fire_simtalk_msg_cb = callback
        if self._event_handler:
            self._event_handler.on_fire_simtalk_message = callback

    def register_on_simulation_error(
        self, callback: Optional[Callable[[SimulationException], None]]
    ):
        self._user_simulation_error_cb = callback

    def _close_event_thread(self):
        """Closes the Event Thread when the instance is terminated."""
        if self._event_thread:
            self._event_thread.join(timeout=1)

    def _event_loop(self):
        """Listen to Events."""
        pythoncom.CoInitialize()
        while self._running:
            pythoncom.PumpWaitingMessages()
            time.sleep(self._event_polling_interval)

    def quit(self) -> None:
        """Quits the current instance."""
        if not self._instance:
            raise Exception("Instance has been closed before already.")

        logger.info(
            f"Closing Siemens Tecnomatix Plant Simulation {self._version.value if isinstance(self._version, PlantsimVersion) else self._version} instance."
        )

        try:
            self._instance.Quit()
        except Exception:
            raise Exception("Instance has been closed before already.")

        del self._instance

    def close_model(self) -> None:
        """Closes the active model"""
        logger.info("Closing model.")
        self._instance.CloseModel()

        self._model_loaded = False
        self._model_path = None
        self._simulation_error = None

    def set_event_controller(self, path: PlantsimPath = None) -> None:
        """
        Sets the path of the Event Controller

        Attributes:
        ----------
        path : str, optional
            Path to the EventController object. If not giveen, it defaults to the defaul relative paths EventController (default: None)
        """
        if path:
            self._event_controller = path
        elif self._network_path:
            self._event_controller = PlantsimPath(self._network_path, "EventController")

    def execute_sim_talk(self, source_code: str, *parameters: any) -> any:
        """
        Executes Sim Talk in the current instance and optionally returns the value returned by Sim Talk

        Attributes:
        ----------
        source_code : str
            The code to be executed
        *parameters : any
            Parameters to pass
        """
        if parameters:
            return self._instance.ExecuteSimTalk(source_code, *parameters)

        return self._instance.ExecuteSimTalk(source_code)

    def get_value(self, path: PlantsimPath) -> Any:
        """
        returns the value of an attribute of a Plant Simulation object

        Attributes:
        ----------
        path : str
            path to the attribute
        """
        value = self._instance.GetValue(str(path))

        return value

    def get_table(self, path: PlantsimPath) -> pd.DataFrame:
        """
        returns a dataframe based on a Plant Simulation table object

        Attributes:
        ----------
        path : str
            path to the table
        """
        # Get data dimensions
        y_dim = self.get_value(PlantsimPath(path, "yDim"))
        x_dim = self.get_value(PlantsimPath(path, "xDim"))

        # Check if indexes are active
        row_index_active = self.get_value(PlantsimPath(path, "rowIndex"))
        index: Optional[List[Any]] = None
        if row_index_active:
            index = [self.get_value(f"{path}[0,{row}]") for row in range(1, y_dim + 1)]

        col_index_active = self.get_value(PlantsimPath(path, "columnIndex"))
        columns: Optional[List[str]] = None
        index_name: Optional[str] = None
        if col_index_active:
            if row_index_active:
                index_name = self.get_value(f"{path}[0,0]")

            columns = [
                self.get_value(f"{path}[{col},0]") for col in range(1, x_dim + 1)
            ]

        data = []
        for row in range(1, y_dim + 1):
            row_data = []
            for col in range(1, x_dim + 1):
                cell_value = self.get_value(f"{path}[{col},{row}]")
                row_data.append(cell_value)
            data.append(row_data)

        df = pd.DataFrame(data, columns=columns, index=index)
        if index_name is not None:
            df.index.name = index_name
        return df

    def get_table_column_data_type(self, table: PlantsimPath, column: int) -> str:
        return self.execute_sim_talk(
            "param t: object, column:integer -> string return t.getDataType(column)",
            table,
            column,
        )

    def set_value(self, path: PlantsimPath, value: Any) -> None:
        """
        Sets a value to a given attribute

        Attributes:
        ----------
        object_name : str
            path to the attribute
        value : any
            the new value the attribute should be assigned to
        is_absolute : bool
            Whether the path to the object is absolute already. If not, the relative path context is going to be used before the oject name
        """
        self._instance.SetValue(str(path), value)

    def set_table(self, path: PlantsimPath, df: pd.DataFrame) -> None:
        """
        Set a Plant Simulation Tabelle based on a DataFrame

        Attribute:
        ----------
        path : str
            path to the table
        df : pd.DataFrame
            DataFrame, which values need to be written
        """
        y_dim, x_dim = df.shape

        col_index_active = self.get_value(PlantsimPath(path, "columnIndex"))
        if col_index_active and df.columns is not None:
            for col, name in enumerate(df.columns, 1):
                self.set_value(f"{path}[{col},0]", name)

        row_index_active = self.get_value(PlantsimPath(path, "rowIndex"))
        if row_index_active and df.index is not None:
            if df.index.name is not None and col_index_active:
                self.set_value(f"{path}[0,0]", df.index.name)
            for row, idx in enumerate(df.index, 1):
                self.set_value(f"{path}[0,{row}]", idx)

        for row in range(1, y_dim + 1):
            for col in range(1, x_dim + 1):
                value = df.iat[row - 1, col - 1]
                self.set_value(f"{path}[{col},{row}]", value)

    def _is_simulation_running(self) -> bool:
        """
        Property holding true, when the simulation is running at the moment, false, when it is not running
        """
        return self._instance.IsSimulationRunning()

    def load_model(
        self, filepath: str, password: str = None, close_other: bool = False
    ) -> None:
        """
        Loading a model into the current instance

        Attributes:
        ----------
        filepath : str
            The full path to the model file (.spp)
        password : str, optional
            designates the password that is used for loading an encrypted model (default is None)
        """
        if close_other:
            self.close_model()

        if self._model_loaded:
            raise Exception("Another model is opened already.")

        if not os.path.exists(filepath):
            raise Exception("File does not exists.")

        logger.info(f"Loading {filepath}.")

        try:
            self._instance.LoadModel(filepath, password if password else None)
        except Exception as e:
            raise PlantsimException(e)

        self._set_datetime_format()

        self._model_loaded = True
        self._model_path = filepath
        self._simulation_error = None

    def _load_simtalk_script(self, script_name: str) -> str:
        """Loads a SimTalk script"""
        package = __package__
        resource = f"sim_talk_scripts/{script_name}.st"
        return importlib.resources.files(package).joinpath(resource).read_text()

    def install_error_handler(self):
        """Installs an error handler in the model file under basis.ErrorHandler. Searches for any method object and duplicates that."""
        simtalk = self._load_simtalk_script("install_error_handler")

        response = self.execute_sim_talk(simtalk)

        if not response:
            raise Exception("Could not create Error Handler")

        self._error_handler = "basis.ErrorHandler"

    def remove_error_handler(self):
        """Removes the installed error handler from basis.ErrorHandler."""
        if not self._error_handler:
            raise Exception("Not error handler has been installed")

        simtalk = self._load_simtalk_script("remove_error_handler")

        response = self.execute_sim_talk(simtalk)

        if not response:
            raise Exception("Could not remove the error handler")

        self._error_handler = None

    def new_model(self, close_other: bool = False) -> None:
        """Creates a new simulation model in the current instance"""
        if close_other:
            self.close_model()

        logger.info("Creating a new model.")
        try:
            self._instance.NewModel()
        except Exception as e:
            raise PlantsimException(e)

        self._simulation_error = None
        self._model_loaded = False

    def open_console_log_file(self, filepath: str) -> None:
        """Routes the Console output to a file"""
        self._instance.OpenConsoleLogFile(filepath)

    def close_console_log_file(self) -> None:
        """Closes the routing to the output file"""
        self._instance.OpenConsoleLogFile("")

    def quit_after_time(self, time: int) -> None:
        """
        Quits the current instance after a specified time

        Attributes:
        ----------
        time : int
            time after the instrance quits in seconds
        """
        self._instance.QuitAfterTime(time)

    def reset_simulation(self) -> None:
        """
        Resets the simulation

        Attributes:
        ----------
        eventcontroller_object : str, optional
            path to the Event Controller object to be reset. If not given, it defaults to the default event controller path (default: None)
        """
        if not self._event_controller:
            raise Exception("EventController needs to be set.")

        self._simulation_error = None
        self._instance.ResetSimulation(self._event_controller)

    def save_model(self, folder_path: str, file_name: str) -> None:
        """
        Saves the current model as the given name in the given folder

        Attributes:
        ----------
        folder_path : str
            path to the folder the model should be saved in
        file_name : str
            Name of the Model
        """
        full_path = str(Path(folder_path, f"{file_name}.spp"))
        logger.info(f"Saving the model to: {full_path}")
        try:
            self._instance.SaveModel(full_path)
        except Exception as e:
            raise PlantsimException(e)

        self._model_path = full_path

    def start_simulation(self, without_animation: bool = False) -> None:
        """
        Starts the simulation
        """
        if not self._event_controller:
            raise Exception("EventController needs to be set.")

        self._simulation_error = None
        self._simulation_finished_event.clear()
        self._simulation_error_event.clear()
        self._instance.StartSimulation(self._event_controller, without_animation)

    def run_simulation(
        self,
        without_animation: bool = True,
        on_init: Optional[Callable[["Plantsim"], None]] = None,
        on_endsim: Optional[Callable[["Plantsim"], None]] = None,
        on_simulation_error: Optional[
            Callable[["Plantsim", SimulationException], None]
        ] = None,
        on_progress: Optional[Callable[["Plantsim", float], None]] = None,
        cancel_event: Optional[threading.Event] = None,
    ) -> None:
        """
        Makes a full simulation run and returns after the run is over. Throws in case the simulation ends without finishing.
        """
        if on_init:
            on_init(self)

        self.start_simulation(without_animation)

        self._run_simulation_event_loop(
            on_progress=on_progress, cancel_event=cancel_event
        )

        while (
            not self._simulation_finished_event.is_set()
            and not self._simulation_error_event.is_set()
        ):
            pythoncom.PumpWaitingMessages()
            time.sleep(self._event_polling_interval)

        if self._simulation_error_event.is_set():
            if on_simulation_error:
                on_simulation_error(self, self._simulation_error_event.error)
                return
            raise self._simulation_error_event.error

        if cancel_event is not None and cancel_event.is_set():
            self.stop_simulation()
            return

        if on_endsim:
            on_endsim(self)

    def _run_simulation_event_loop(
        self,
        on_progress: Optional[Callable[["Plantsim", float], None]] = None,
        cancel_event: Optional[threading.Event] = None,
    ):
        """"""
        start_date = self.get_start_date()
        end_time = self.get_end_time()
        last_progress_update = time.time()

        while (
            not self._simulation_finished_event.is_set()
            and not self._simulation_error_event.is_set()
            and (cancel_event is None or not cancel_event.is_set())
        ):
            pythoncom.PumpWaitingMessages()
            time.sleep(self._event_polling_interval)

            if on_progress:
                now = time.time()
                if now - last_progress_update >= 1:
                    last_progress_update = now
                    current_simulation_time = self.get_abs_sim_time()
                    progress = ((current_simulation_time - start_date) / end_time) * 100
                    on_progress(self, progress)

    def get_abs_sim_time(self) -> datetime:
        """Gets the current simulation time"""
        if not self._event_controller:
            raise Exception("EventController needs to be set.")

        return self._str_to_datetime(
            self.get_value(PlantsimPath(self._event_controller, "AbsSimTime"))
        )

    def _str_to_datetime(self, date_str: str) -> datetime:
        """Converts a string into a datetime"""
        return datetime.strptime(date_str, self._datetime_format)

    def get_start_date(self) -> datetime:
        """Extracts the start date from the event controller."""
        if not self._event_controller:
            raise Exception("EventController needs to be set.")

        attribute_name = "StartDate"
        if self._version < Version(PlantsimVersion.V_MJ_25_MI_4.value):
            attribute_name = "Date"

        return self._str_to_datetime(
            self.get_value(PlantsimPath(self._event_controller, attribute_name))
        )

    def get_model_language(self) -> int:
        """Returns the model language."""
        return self.execute_sim_talk("-> integer return language()")

    def _set_datetime_format(self) -> None:
        """Sets the datetime format based on the the loaded model."""
        language = self.get_model_language()

        match language:
            case 0:  # German
                self._datetime_format = "%d.%m.%Y %H:%M:%S.%f"
            case 1:  # English
                self._datetime_format = "%Y-%m-%d %H:%M:%S.%f"
            case _:
                raise NotImplementedError()

    def get_end_time(self) -> timedelta:
        """Extracts the end time of the event controller."""
        if not self._event_controller:
            raise Exception("EventController needs to be set.")

        attribute_name = "EndTime"
        if self._version < Version(PlantsimVersion.V_MJ_25_MI_4.value):
            attribute_name = "End"

        return timedelta(
            seconds=self.get_value(PlantsimPath(self._event_controller, attribute_name))
        )

    def stop_simulation(self) -> None:
        """
        Stops the simulation

        Attributes:
        ----------
        eventcontroller_object : str, optional
            path to the Event Controller object to be reset. If not given, it defaults to the default event controller path (default: None)
        """
        if not self._event_controller:
            raise Exception("EventController needs to be set.")

        self._instance.StopSimulation(self._event_controller)

    def set_seed(self, seed: int) -> None:
        """Sets the Seed on the event controller."""
        if not self._event_controller:
            raise Exception("EventController needs to be set")

        if seed > 2147483647 or seed < -2147483647:
            raise Exception("Seed must be between -2147483647 and 2147483647")

        self.set_value(
            PlantsimPath(self._event_controller, "RandomNumbersVariant"), seed
        )

    @property
    def simulation_running(self) -> bool:
        """Returns if the simulation is currently running."""
        return self._is_simulation_running()

    @property
    def model_loaded(self) -> bool:
        """Attribute holding true, when the instance has a model loaded, false, when it not"""
        return self._model_loaded

    @property
    def model_path(self) -> Union[str, None]:
        """Attribute holding the path to current model file"""
        return self._model_path

    @property
    def network_path(self) -> Union[str, None]:
        """Attribute holding the current active network path"""
        return self._network_path

    @property
    def visible(self) -> bool:
        """Attribute holding true, when the instance is visible, false, when it's not"""
        return self._visible

    @property
    def trusted(self) -> bool:
        """Attribute holding true, when the instance is trusted, false, when it's not"""
        return self._trusted

    @property
    def suppress_3d(self) -> bool:
        """Attribute holding true, when the instance is suppressed, false, when it's not"""
        return self._suppress_3d

    @property
    def license(self) -> Union[PlantsimLicense, str]:
        """Attribute holding the license of the current instance"""
        return self._license

    @property
    def version(self) -> Union[PlantsimVersion, str]:
        """Attribute holding the version of the current instance"""
        return self._version

    @property
    def show_msg_box(self) -> bool:
        """Attribute holding true, when the instance is showing a message box, false, when it's not"""
        return self._show_msg_box

    # Experimentals
    def get_current_process_id(self) -> int:
        """
        Returns the ID of the current instance. Not sure what the id is for yet.
        """
        return self._instance.GetCurrentProcessId()

    def get_ids_of_names(self):
        """
        Further documentation: https://docs.microsoft.com/en-us/windows/win32/api/oaidl/nf-oaidl-idispatch-getidsofnames
        """
        return self._instance.GetIDsOfNames(".Models.Model.Eventcontroller")

    def get_jte_export(self):
        """
        Takes one argument. An object in the simulation. Gives the 3D JTE Export. Not sure how it works yet.
        """
        return self._instance.GetJTExport()

    def get_type_info(self):
        """Takes one argument"""
        return self._instance.GetTypeInfo()

    def get_type_info_count(self):
        return self._instance.GetTypeInfoCount()

    def has_simulation_error(self):
        return self._instance.HasSimulationError()

    def invoke(self):
        return self._instance.Invoke()

    def load_model_without_state(self):
        return self._instance.LoadModelWithoutState()

    def query_interface(self):
        return self._instance.QueryInterface()

    def release(self):
        return self._instance.Release()

    def set_crash_stack_file(self):
        return self._instance.SetCrashStackFile()

    def set_stop_simulation_on_error(self):
        return self._instance.SetStopSimulationOnError()

    def tranfer_model(self):
        return self._instance.TransferModel()
