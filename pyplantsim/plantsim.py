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

    :ivar _dispatch_id: COM dispatch identifier for the RemoteControl interface.
    :vartype _dispatch_id: str
    :ivar _event_controller: Path to the event controller.
    :vartype _event_controller: PlantsimPath
    :ivar _version: Plant Simulation version to be used.
    :vartype _version: PlantsimVersion or str
    :ivar _visible: Whether the instance window is visible.
    :vartype _visible: bool
    :ivar _trusted: Whether the instance has access to the computer.
    :vartype _trusted: bool
    :ivar _license: License to be used.
    :vartype _license: PlantsimLicense or str
    :ivar _suppress_3d: Suppresses the start of the 3D view.
    :vartype _suppress_3d: bool
    :ivar _show_msg_box: Whether to show a message box.
    :vartype _show_msg_box: bool
    :ivar _network_path: Network path.
    :vartype _network_path: str
    :ivar _event_thread: Event thread object.
    :ivar _event_handler: Handler for Plant Simulation events.
    :vartype _event_handler: PlantSimEvents
    :ivar _event_polling_interval: Interval for polling events.
    :vartype _event_polling_interval: float
    :ivar _datetime_format: Format for datetime strings.
    :vartype _datetime_format: str
    :ivar _model_loaded: Whether a model has been loaded.
    :vartype _model_loaded: bool
    :ivar _model_path: Path to the loaded model.
    :vartype _model_path: str
    :ivar _running: Simulation status.
    :vartype _running: str
    :ivar _simulation_error: Simulation error details.
    :vartype _simulation_error: Optional[dict]
    :ivar _simulation_finished_event: Event triggered when the simulation finishes.
    :vartype _simulation_finished_event: threading.Event
    :ivar _error_handler: The path to the installed error handler.
    :vartype _error_handler: Optional[str]
    :ivar _user_simulation_finished_cb: Callback for when the simulation finishes.
    :vartype _user_simulation_finished_cb: Optional[Callable[[], None]]
    :ivar _user_simtalk_msg_cb: Callback for SimTalk messages.
    :vartype _user_simtalk_msg_cb: Optional[Callable[[str], None]]
    :ivar _user_fire_simtalk_msg_cb: Callback to fire SimTalk messages.
    :vartype _user_fire_simtalk_msg_cb: Optional[Callable[[str], None]]
    :ivar _user_simulation_error_cb: Callback for simulation errors.
    :vartype _user_simulation_error_cb: Optional[Callable[[SimulationException], None]]
    """

    # Defaults
    _DISPATCH_ID: str = "Tecnomatix.PlantSimulation.RemoteControl"
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
        Initialize the Siemens Tecnomatix Plant Simulation instance.

        :param version: Plant Simulation version to use.
        :type version: PlantsimVersion or str, optional
        :param visible: Whether the instance window is visible.
        :type visible: bool, optional
        :param trusted: Whether the instance should have access to the computer.
        :type trusted: bool, optional
        :param license: License to use.
        :type license: PlantsimLicense or str, optional
        :param suppress_3d: Suppress the start of 3D view.
        :type suppress_3d: bool, optional
        :param show_msg_box: Show a message box.
        :type show_msg_box: bool, optional
        :param simulation_finished_callback: Callback function when simulation finishes.
        :type simulation_finished_callback: Callable[[], None], optional
        :param simtalk_msg_callback: Callback for received SimTalk messages.
        :type simtalk_msg_callback: Callable[[str], None], optional
        :param fire_simtalk_msg_callback: Callback to trigger SimTalk messages.
        :type fire_simtalk_msg_callback: Callable[[str], None], optional
        :param simulation_error_callback: Callback for simulation errors.
        :type simulation_error_callback: Callable[[SimulationException], None], optional
        :param event_polling_interval: Interval (in seconds) for polling events.
        :type event_polling_interval: float, optional
        :param disable_log_message: Disable log messages.
        :type disable_log_message: bool, optional
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
        """
        Set the Plant Simulation version.

        :param version: Plant Simulation version or string.
        :type version: Union[PlantsimVersion, str]
        """
        self._version = Version(
            version.value if isinstance(version, PlantsimVersion) else version
        )

    def __enter__(self) -> "Plantsim":
        """
        Enter the runtime context for the PlantSim instance.

        :return: The PlantSim instance.
        :rtype: Plantsim
        """
        return self

    def __repr__(self) -> str:
        """
        Return the string representation of the PlantSim instance.

        :return: String representation.
        :rtype: str
        """
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
        """
        Start the Plant Simulation instance.

        :raises Exception: If Plant Simulation is already running.
        :return: The PlantSim instance.
        :rtype: Plantsim
        """
        if self._running:
            raise Exception("Plant Simulation already running.")

        logger.info(
            f"Starting Siemens Tecnomatix Plant Simulation {str(self._version)} instance."
        )

        # Changing dispatch_id regarding requested version
        self._dispatch_id = self._DISPATCH_ID
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

        # Should the instance window be visible on screen
        self.set_visible(self._visible, force=True)

        # Set license
        try:
            self.set_license(self._license, force=True)
        except Exception as e:
            self.quit()
            raise PlantsimException(e)

        # Should the instance have access to the computer or not
        self.set_trust_models(self._trusted, force=True)

        # Should the instance suppress the start of 3D
        self.set_suppress_start_of_3d(self._suppress_3d, force=True)

        # Should the instance show a message box
        self.set_show_message_box(self._show_msg_box, force=True)

        return self

    def __exit__(self, _, __, ___) -> None:
        """
        Exit the runtime context and stop the Plant Simulation instance.
        """
        self.stop()

    def stop(self) -> None:
        """
        Stop the Plant Simulation instance and clean up resources.
        """
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
        """
        Set the active network.

        :param path: Network path.
        :type path: PlantsimPath
        :param set_event_controller: Whether to set the event controller.
        :type set_event_controller: bool, optional
        :param install_error_handler: Whether to install the error handler.
        :type install_error_handler: bool, optional
        """
        self._network_path = path
        self._instance.SetPathContext(str(self._network_path))

        if install_error_handler:
            self.install_error_handler()

        if set_event_controller:
            self.set_event_controller()

    def set_show_message_box(self, show: bool, force=False) -> None:
        """
        Set whether the instance should show a message box.

        :param show: Show message box.
        :type show: bool
        :param force: Force update even if value is already set.
        :type force: bool, optional
        """
        if self._show_msg_box != show or force:
            self._show_msg_box = show
            self._instance.SetNoMessageBox(self._show_msg_box)

    def set_suppress_start_of_3d(self, suppress: bool, force=False) -> None:
        """
        Set whether to suppress the start of 3D.

        :param suppress: Suppress 3D view.
        :type suppress: bool
        :param force: Force update even if value is already set.
        :type force: bool, optional
        """
        if self._suppress_3d != suppress or force:
            self._suppress_3d = suppress
            self._instance.SetSuppressStartOf3D(self._suppress_3d)

    def set_license(self, license: PlantsimLicense, force=False) -> None:
        """
        Set the license for the instance.

        :param license: License type.
        :type license: PlantsimLicense
        :param force: Force update even if value is already set.
        :type force: bool, optional
        """
        if self._license != license or force:
            self._license = license

            self._instance.SetLicenseType(
                self._license.value
                if isinstance(self._license, PlantsimLicense)
                else self._license
            )

    def set_visible(self, visible: bool, force=False) -> None:
        """
        Set whether the instance window is visible.

        :param visible: Window visibility.
        :type visible: bool
        :param force: Force update even if value is already set.
        :type force: bool, optional
        """
        if self._visible != visible or force:
            self._visible = visible
            self._instance.SetVisible(self._visible)

    def set_trust_models(self, trusted: bool, force=False) -> None:
        """
        Set whether the instance has access to the computer.

        :param trusted: Trusted mode.
        :type trusted: bool
        :param force: Force update even if value is already set.
        :type force: bool, optional
        """
        if self._trusted != trusted or force:
            self._trusted = trusted
            self._instance.SetTrustModels(self._trusted)

    def _start_event_thread(self):
        """
        Start the event thread to listen to COM Events.
        """
        self._event_thread = threading.Thread(target=self._event_loop, daemon=True)
        self._event_thread.start()

    def _internal_simulation_finished(self):
        """
        Gets called when the simulation finishes.
        """
        self._simulation_finished_event.set()
        if self._user_simulation_finished_cb:
            self._user_simulation_finished_cb()

    def register_on_simulation_finished(self, callback: Optional[Callable[[], None]]):
        """
        Set callback for OnSimulationFinished event.

        :param callback: Callback function.
        :type callback: Optional[Callable[[], None]]
        """
        self._user_simulation_finished_cb = callback

    def _internal_on_simtalk_message(self, msg: str):
        """
        Gets called when the model sends a SimTalk message.

        :param msg: SimTalk message.
        :type msg: str
        """
        if self._is_json(msg):
            self._handle_simtalk_message(msg)

        if self._user_simtalk_msg_cb:
            self._user_simtalk_msg_cb(msg)

    def _handle_simtalk_message(self, msg: str):
        """
        Handle a SimTalk message.

        :param msg: SimTalk message in JSON format.
        :type msg: str
        """
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
        """
        Check if message is valid JSON.

        :param msg: Message string.
        :type msg: str
        :return: True if valid JSON, else False.
        :rtype: bool
        """
        try:
            json.loads(msg)
        except ValueError:
            return False
        return True

    def register_on_simtalk_message(self, callback: Optional[Callable[[str], None]]):
        """
        Set callback for OnSimTalkMessage event.

        :param callback: Callback function.
        :type callback: Optional[Callable[[str], None]]
        """
        self._user_simtalk_msg_cb = callback

    def register_on_fire_simtalk_message(
        self, callback: Optional[Callable[[str], None]]
    ):
        """
        Set callback for FireSimTalkMessage event.

        :param callback: Callback function.
        :type callback: Optional[Callable[[str], None]]
        """
        self._user_fire_simtalk_msg_cb = callback
        if self._event_handler:
            self._event_handler.on_fire_simtalk_message = callback

    def register_on_simulation_error(
        self, callback: Optional[Callable[[SimulationException], None]]
    ):
        """
        Set callback for simulation errors.

        :param callback: Callback function.
        :type callback: Optional[Callable[[SimulationException], None]]
        """
        self._user_simulation_error_cb = callback

    def _close_event_thread(self):
        """
        Close the event thread when the instance is terminated.
        """
        if self._event_thread:
            self._event_thread.join(timeout=1)

    def _event_loop(self):
        """
        Listen to events and handle COM messages.
        """
        pythoncom.CoInitialize()
        while self._running:
            pythoncom.PumpWaitingMessages()
            time.sleep(self._event_polling_interval)

    def quit(self) -> None:
        """
        Quit the current Plant Simulation instance.

        :raises Exception: If instance is already closed.
        """
        if not self._instance:
            raise Exception("Instance has been closed before already.")

        logger.info(
            f"Closing Siemens Tecnomatix Plant Simulation {self._version.value if isinstance(self._version, PlantsimVersion) else self._version} instance."
        )

        try:
            self._instance.Quit()
        except Exception:
            raise Exception("Instance has been closed before already.")

        self._instance = None

    def close_model(self) -> None:
        """
        Close the active model.
        """
        logger.info("Closing model.")
        self._instance.CloseModel()

        self._model_loaded = False
        self._model_path = None
        self._simulation_error = None

    def set_event_controller(self, path: PlantsimPath = None) -> None:
        """
        Set the path of the Event Controller.

        :param path: Path to the EventController object. If not given, uses default.
        :type path: str, optional
        """
        if path:
            self._event_controller = path
        elif self._network_path:
            self._event_controller = PlantsimPath(self._network_path, "EventController")

    def execute_sim_talk(self, source_code: str, *parameters: any) -> any:
        """
        Execute SimTalk in the current instance and return the result.

        :param source_code: The code to be executed.
        :type source_code: str
        :param parameters: Parameters to pass to SimTalk.
        :type parameters: any
        :return: Result of SimTalk execution.
        :rtype: any
        """
        if parameters:
            return self._instance.ExecuteSimTalk(source_code, *parameters)

        return self._instance.ExecuteSimTalk(source_code)

    def get_value(self, path: PlantsimPath) -> Any:
        """
        Get the value of an attribute of a Plant Simulation object.

        :param path: Path to the attribute.
        :type path: str
        :return: Attribute value.
        :rtype: Any
        """
        value = self._instance.GetValue(str(path))

        return value

    def get_table(self, path: PlantsimPath) -> pd.DataFrame:
        """
        Get a DataFrame based on a Plant Simulation table object.

        :param path: Path to the table.
        :type path: str
        :return: DataFrame representing the table.
        :rtype: pd.DataFrame
        """
        # Get data dimensions
        y_dim = self.get_value(PlantsimPath(path, "yDim"))
        x_dim = self.get_value(PlantsimPath(path, "xDim"))

        # Check if indexes are active
        row_index_active = self.get_value(PlantsimPath(path, "rowIndex"))
        index: Optional[List[Any]] = None
        if row_index_active:
            index = [
                self.get_value(PlantsimPath(path, f"[0,{row}]"))
                for row in range(1, y_dim + 1)
            ]

        col_index_active = self.get_value(PlantsimPath(path, "columnIndex"))
        columns: Optional[List[str]] = None
        index_name: Optional[str] = None
        if col_index_active:
            if row_index_active:
                index_name = self.get_value(PlantsimPath(path, "[0,0]"))

            columns = [
                self.get_value(PlantsimPath(path, f"[{col},0]"))
                for col in range(1, x_dim + 1)
            ]

        data = []
        for row in range(1, y_dim + 1):
            row_data = []
            for col in range(1, x_dim + 1):
                cell_value = self.get_value(PlantsimPath(path, f"[{col},{row}]"))
                row_data.append(cell_value)
            data.append(row_data)

        df = pd.DataFrame(data, columns=columns, index=index)
        if index_name is not None:
            df.index.name = index_name
        return df

    def get_table_column_data_type(self, table: PlantsimPath, column: int) -> str:
        """
        Get the data type of a table column.

        :param table: Table path.
        :type table: PlantsimPath
        :param column: Column index.
        :type column: int
        :return: Data type as string.
        :rtype: str
        """
        simtalk = self._load_simtalk_script("get_table_column_data_type")
        return self.execute_sim_talk(simtalk, table, column)

    def set_value(self, path: PlantsimPath, value: Any) -> None:
        """
        Set a value to a given attribute.

        :param path: Path to the attribute.
        :type path: str
        :param value: The new value to assign.
        :type value: any
        """
        self._instance.SetValue(str(path), value)

    def set_table(self, path: PlantsimPath, df: pd.DataFrame) -> None:
        """
        Set a Plant Simulation table based on a DataFrame.

        :param path: Path to the table.
        :type path: str
        :param df: DataFrame containing the values to write.
        :type df: pd.DataFrame
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
        Check if the simulation is currently running.

        :return: True if running, False otherwise.
        :rtype: bool
        """
        return self._instance.IsSimulationRunning()

    def load_model(
        self, filepath: str, password: str = None, close_other: bool = False
    ) -> None:
        """
        Load a model into the current instance.

        :param filepath: Full path to the model file (.spp).
        :type filepath: str
        :param password: Password for encrypted models.
        :type password: str, optional
        :param close_other: Close other models before loading.
        :type close_other: bool, optional
        :raises Exception: If file does not exist or another model is loaded.
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
        """
        Load a SimTalk script from resources.

        :param script_name: Name of the SimTalk script.
        :type script_name: str
        :return: SimTalk script content.
        :rtype: str
        """
        package = __package__
        resource = f"sim_talk_scripts/{script_name}.st"
        return importlib.resources.files(package).joinpath(resource).read_text()

    def install_error_handler(self):
        """
        Install an error handler in the model file under basis.ErrorHandler. Searches for any method object and duplicates that.

        :raises Exception: If error handler could not be created.
        """
        simtalk = self._load_simtalk_script("install_error_handler")

        response = self.execute_sim_talk(simtalk)

        if not response:
            raise Exception("Could not create Error Handler")

        self._error_handler = "basis.ErrorHandler"

    def remove_error_handler(self):
        """
        Remove the installed error handler from basis.ErrorHandler.

        :raises Exception: If no error handler is installed or removal fails.
        """
        if not self._error_handler:
            raise Exception("Not error handler has been installed")

        simtalk = self._load_simtalk_script("remove_error_handler")

        response = self.execute_sim_talk(simtalk)

        if not response:
            raise Exception("Could not remove the error handler")

        self._error_handler = None

    def new_model(self, close_other: bool = False) -> None:
        """
        Create a new simulation model in the current instance.

        :param close_other: Close other models before creating new one.
        :type close_other: bool, optional
        """
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
        """
        Route the Console output to a file.

        :param filepath: Path to the log file.
        :type filepath: str
        """
        self._instance.OpenConsoleLogFile(filepath)

    def close_console_log_file(self) -> None:
        """
        Close routing to the output file.
        """
        self._instance.OpenConsoleLogFile("")

    def quit_after_time(self, time: int) -> None:
        """
        Quit the current instance after a specified time.

        :param time: Time in seconds after which instance quits.
        :type time: int
        """
        self._instance.QuitAfterTime(time)

    def reset_simulation(self) -> None:
        """
        Reset the simulation.

        :raises Exception: If EventController is not set.
        """
        if not self._event_controller:
            raise Exception("EventController needs to be set.")

        self._simulation_error = None
        self._instance.ResetSimulation(self._event_controller)

    def save_model(self, folder_path: str, file_name: str) -> None:
        """
        Save the current model under the given name in the given folder.

        :param folder_path: Path to the folder.
        :type folder_path: str
        :param file_name: Name of the model.
        :type file_name: str
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
        Start the simulation.

        :param without_animation: Run without animation.
        :type without_animation: bool, optional
        :raises Exception: If EventController is not set.
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
        Run a full simulation and return after the run is over. This method suggests, that the EventController has a EndDate

        :param without_animation: Run without animation.
        :type without_animation: bool, optional
        :param on_init: Callback before simulation starts.
        :type on_init: Optional[Callable[[Plantsim], None]]
        :param on_endsim: Callback after simulation ends.
        :type on_endsim: Optional[Callable[[Plantsim], None]]
        :param on_simulation_error: Callback on simulation error.
        :type on_simulation_error: Optional[Callable[[Plantsim, SimulationException], None]]
        :param on_progress: Progress callback (receives percent complete).
        :type on_progress: Optional[Callable[[Plantsim, float], None]]
        :param cancel_event: Event to cancel the run.
        :type cancel_event: Optional[threading.Event]
        :raises SimulationException: If a simulation error occurs.
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
        """
        Internal loop to handle simulation events and progress callbacks.

        :param on_progress: Progress callback.
        :type on_progress: Optional[Callable[[Plantsim, float], None]]
        :param cancel_event: Event to cancel the simulation.
        :type cancel_event: Optional[threading.Event]
        """
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
        """
        Get the current simulation absolute time.

        :return: Current simulation time.
        :rtype: datetime
        :raises Exception: If EventController is not set.
        """
        if not self._event_controller:
            raise Exception("EventController needs to be set.")

        return self._str_to_datetime(
            self.get_value(PlantsimPath(self._event_controller, "AbsSimTime"))
        )

    def _str_to_datetime(self, date_str: str) -> datetime:
        """
        Convert a string into a datetime object.

        :param date_str: Date string.
        :type date_str: str
        :return: Parsed datetime object.
        :rtype: datetime
        """
        return datetime.strptime(date_str, self._datetime_format)

    def get_start_date(self) -> datetime:
        """
        Extract the start date from the event controller.

        :return: Start datetime.
        :rtype: datetime
        :raises Exception: If EventController is not set.
        """
        if not self._event_controller:
            raise Exception("EventController needs to be set.")

        attribute_name = "StartDate"
        if self._version < Version(PlantsimVersion.V_MJ_25_MI_4.value):
            attribute_name = "Date"

        return self._str_to_datetime(
            self.get_value(PlantsimPath(self._event_controller, attribute_name))
        )

    def get_model_language(self) -> int:
        """
        Get the model language.

        :return: Language code (0=German, 1=English, 3=Chinese).
        :rtype: int
        """
        simtalk = self._load_simtalk_script("get_model_language")
        return self.execute_sim_talk(simtalk)

    def _set_datetime_format(self) -> None:
        """
        Set the datetime format based on the loaded model's language.

        :raises NotImplementedError: If language is not supported.
        """
        language = self.get_model_language()

        match language:
            case 0:  # German
                self._datetime_format = "%d.%m.%Y %H:%M:%S.%f"
            case 1:  # English
                self._datetime_format = "%Y-%m-%d %H:%M:%S.%f"
            case 3:  # Chinese
                self._datetime_format = "%Y/%m/%d %H:%M:%S.%f"
            case _:
                raise NotImplementedError()

    def get_end_time(self) -> timedelta:
        """
        Extract the end time of the event controller.

        :return: Simulation end time as timedelta.
        :rtype: timedelta
        :raises Exception: If EventController is not set.
        """
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
        Stop the simulation.

        :raises Exception: If EventController is not set.
        """
        if not self._event_controller:
            raise Exception("EventController needs to be set.")

        self._instance.StopSimulation(self._event_controller)

    def set_seed(self, seed: int) -> None:
        """
        Set the random seed on the event controller.

        :param seed: Seed value (-2147483647 to 2147483647).
        :type seed: int
        :raises Exception: If EventController is not set or seed is out of range.
        """
        if not self._event_controller:
            raise Exception("EventController needs to be set")

        if seed > 2147483647 or seed < -2147483647:
            raise Exception("Seed must be between -2147483647 and 2147483647")

        self.set_value(
            PlantsimPath(self._event_controller, "RandomNumbersVariant"), seed
        )

    def exists_path(self, path: Union[PlantsimPath, str]) -> bool:
        """
        Check if the given path exists in the loaded model.

        :param path: Path to check.
        :type path: Union[PlantsimPath, str]
        :return: True if path exists, False otherwise.
        :rtype: bool
        :raises Exception: If no model is loaded.
        """
        if not self.model_loaded:
            raise Exception("No model is loaded.")

        simtalk = self._load_simtalk_script("exists_path")
        return self.execute_sim_talk(simtalk, path)

    def restart(self) -> None:
        """
        Restart the Plant Simulation instance and restore previous state.

        :raises NotImplementedError: Restart is not implemented.
        """
        raise NotImplementedError("This is not working yet.")
        old_model_loaded = self.model_loaded
        old_model_path = self.model_path
        old_network_path = self.network_path
        old_event_controller = self._event_controller
        old_error_handler = self._error_handler

        self.stop()
        self.start()

        # Wiederherstellen
        if old_model_loaded and old_model_path:
            self.load_model(old_model_path)

        if old_network_path:
            self.set_network(old_network_path)

        if old_event_controller:
            self.set_event_controller(old_event_controller)

        if old_error_handler:
            self.install_error_handler()

    @property
    def simulation_running(self) -> bool:
        """
        Whether the simulation is currently running.

        :return: True if running, False otherwise.
        :rtype: bool
        """
        return self._is_simulation_running()

    @property
    def model_loaded(self) -> bool:
        """
        Whether the instance has a model loaded.

        :return: True if model is loaded, False otherwise.
        :rtype: bool
        """
        return self._model_loaded

    @property
    def model_path(self) -> Union[str, None]:
        """
        Path to the current model file.

        :return: Model path or None.
        :rtype: Union[str, None]
        """
        return self._model_path

    @property
    def network_path(self) -> Union[str, None]:
        """
        Current active network path.

        :return: Network path or None.
        :rtype: Union[str, None]
        """
        return self._network_path

    @property
    def visible(self) -> bool:
        """
        Whether the instance is visible.

        :return: True if visible, False otherwise.
        :rtype: bool
        """
        return self._visible

    @property
    def trusted(self) -> bool:
        """
        Whether the instance is trusted.

        :return: True if trusted, False otherwise.
        :rtype: bool
        """
        return self._trusted

    @property
    def suppress_3d(self) -> bool:
        """
        Whether suppression of 3D is enabled.

        :return: True if suppressed, False otherwise.
        :rtype: bool
        """
        return self._suppress_3d

    @property
    def license(self) -> Union[PlantsimLicense, str]:
        """
        License of the current instance.

        :return: License type.
        :rtype: Union[PlantsimLicense, str]
        """
        return self._license

    @property
    def version(self) -> Union[PlantsimVersion, str]:
        """
        Version of the current instance.

        :return: Plant Simulation version.
        :rtype: Union[PlantsimVersion, str]
        """
        return self._version

    @property
    def show_msg_box(self) -> bool:
        """
        Whether the instance is showing a message box.

        :return: True if message box is shown, False otherwise.
        :rtype: bool
        """
        return self._show_msg_box

    # Experimentals
    def get_current_process_id(self) -> int:
        """
        Get the ID of the current instance process.

        :return: Process ID.
        :rtype: int
        """
        return self._instance.GetCurrentProcessId()

    def get_ids_of_names(self):
        """
        Get IDs of names for dispatch interface.
        Further documentation: https://docs.microsoft.com/en-us/windows/win32/api/oaidl/nf-oaidl-idispatch-getidsofnames

        :return: IDs of names.
        """
        return self._instance.GetIDsOfNames(".Models.Model.Eventcontroller")

    def get_jte_export(self):
        """
        Get the 3D JTE export for a simulation object.

        :return: 3D JTE export.
        """
        return self._instance.GetJTExport()

    def get_type_info(self):
        """
        Get type information for the instance.

        :return: Type info.
        """
        return self._instance.GetTypeInfo()

    def get_type_info_count(self):
        """
        Get the type information count.

        :return: Type info count.
        """
        return self._instance.GetTypeInfoCount()

    def has_simulation_error(self):
        """
        Check if a simulation error has occurred.

        :return: True if there is an error, False otherwise.
        """
        return self._instance.HasSimulationError()

    def invoke(self):
        """
        Invoke method on the COM instance.
        """
        return self._instance.Invoke()

    def load_model_without_state(self):
        """
        Load a model without restoring state.
        """
        return self._instance.LoadModelWithoutState()

    def query_interface(self):
        """
        Query the COM interface.
        """
        return self._instance.QueryInterface()

    def release(self):
        """
        Release the COM instance.
        """
        return self._instance.Release()

    def set_crash_stack_file(self):
        """
        Set the crash stack file for error logging.
        """
        return self._instance.SetCrashStackFile()

    def set_stop_simulation_on_error(self):
        """
        Set option to stop simulation on error.
        """
        return self._instance.SetStopSimulationOnError()

    def tranfer_model(self):
        """
        Transfer the model to another instance.
        """
        return self._instance.TransferModel()
