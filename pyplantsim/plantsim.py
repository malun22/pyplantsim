import os
from pathlib import Path
import win32com.client

from typing import Union
from loguru import logger

from pyplantsim.versions import PlantsimVersion
from pyplantsim.licenses import PlantsimLicense
from pyplantsim.exception import PlantsimException
from pyplantsim.path import PlantsimPath


class Plantsim:
    """
    A wrapper class for Siemens Tecnomatix Plant Simulation COM Interface

    Attributes:
    ----------
    version : PlantsimVersion or str
        the version to be used (default PlantsimVersion.V_MJ_22_MI_1)
    visible : bool
        whether the instance window be visible on screen (default True)
    trusted : bool
        whether the instance should have access to the computer or not (default True)
    license : PlantsimLicense
        the license to be used (default PlantsimLicense.VIEWER)
    suppress_3d : bool
        whether the instance should suppress the start of 3D (default False)
    show_msg_box : bool 
        whether the instance should show a message box (default False)
    """

    # Defaults
    _dispatch_id: str = "Tecnomatix.PlantSimulation.RemoteControl"
    _event_controller: PlantsimPath = None
    _version: Union[PlantsimVersion, str] = None
    _visible: bool = None
    _trusted: bool = None
    _license: Union[PlantsimLicense, str] = None
    _suppress_3d: bool = None
    _show_msg_box: bool = None
    _relative_path: str = None

    # State management
    _model_loaded: bool = False

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        if self._instance:
            self.quit()

    def __enter__(self):
        logger.info(
            f"Initializing Siemens Tecnomatix Plant Simulation {self._version.value if isinstance(self._version, PlantsimVersion) else self._version} instance.")

        # Changing dispatch_id regarding requested version
        if self._version:
            self._dispatch_id += f".{self._version.value if isinstance(self._version, PlantsimVersion) else self._version}"

        try:
            self._instance = win32com.client.Dispatch(self._dispatch_id)
        except Exception as e:
            raise PlantsimException(e)

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

    def __init__(self, version: Union[PlantsimVersion, str] = PlantsimVersion.V_MJ_22_MI_1, visible: bool = True, trusted: bool = True,
                 license: Union[PlantsimLicense, str] = PlantsimLicense.VIEWER, suppress_3d: bool = False, show_msg_box: bool = False) -> None:
        """
        Initializes the Siemens Tecnomatix Plant Simulation instance.

        Attributes:
        ----------
        version : PlantsimVersion
            the version to be used (default PlantsimVersion.V_MJ_22_MI_1)
        visible : bool
            whether the instance window be visible on screen (default True)
        trusted : bool
            whether the instance should have access to the computer or not (default True)
        license : PlantsimLicense
            the license to be used (default PlantsimLicense.VIEWER)
        suppress_3d : bool
            whether the instance should suppress the start of 3D (default False)
        show_msg_box : bool 
            whether the instance should show a message box (default False)
        """

        # Inits
        self._version: PlantsimVersion = version
        self._visible = visible
        self._trusted = trusted
        self._license = license
        self._suppress_3d = suppress_3d
        self._show_msg_box = show_msg_box

    def set_path_context(self, path: PlantsimPath, force=False) -> None:
        """Sets the relative path. (For instance .Models.Model)"""
        if self._relative_path != path or force:
            self._relative_path = path
            self._instance.SetPathContext(str(self._relative_path))

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

            self._instance.SetLicenseType(self._license.value if isinstance(
                self._license, PlantsimLicense) else self._license)

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

    def quit(self) -> None:
        """Quits the current instance."""
        if not self._instance:
            raise Exception("Instance has been closed before already.")

        logger.info(
            f"Closing Siemens Tecnomatix Plant Simulation {self._version.value if isinstance(self._version, PlantsimVersion) else self._version} instance.")

        try:
            self._instance.Quit()
        except Exception as e:
            raise Exception("Instance has been closed before already.")

        del(self._instance)

    def close_model(self) -> None:
        """Closes the active model"""
        logger.info(f"Closing model.")
        self._instance.CloseModel()

    def set_eventcontroller(self, path: PlantsimPath = None) -> None:
        """
        Sets the path of the Event Controller

        Attributes:
        ----------
        path : str, optional
            Path to the EventController object. If not giveen, it defaults to the defaul relative paths EventController (default: None)
        """
        if path:
            self._event_controller = path
        elif self._relative_path:
            self._event_controller = PlantsimPath(
                self._relative_path, "EventController")

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
        return self._instance.ExecuteSimTalk(source_code, parameters)

    def get_value(self, object_name: PlantsimPath, is_absolute: bool = False) -> any:
        """
        returns the value of an attribute of a Plant Simulation object

        Attributes:
        ----------
        object_name : str
            path to the attribute
        is_absolute : bool
            Whether the path to the object is absolute already. If not, the relative path context is going to be used before the oject name
        """
        return self._instance.GetValue(str(object_name) if is_absolute else str(
            PlantsimPath(self._relative_path, object_name)))

    def set_value(self, object_name: PlantsimPath, value: any, is_absolute: bool = False) -> None:
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
        self._instance.SetValue(str(object_name) if is_absolute else str(
            PlantsimPath(self._relative_path, object_name)), value)

    def is_simulation_running(self) -> bool:
        """
        Property holding true, when the simulation is running at the moment, false, when it is not running
        """
        return self._instance.IsSimulationRunning()

    def load_model(self, filepath: str, password: str = None, close_other: bool = False) -> None:
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

        if not os.path.exists(filepath):
            raise Exception("File does not exists.")

        logger.info(f"Loading {filepath}.")

        try:
            self._instance.LoadModel(filepath, password if password else None)
        except Exception as e:
            raise PlantsimException(e)

    def new_model(self, close_other: bool = False) -> None:
        """Creates a new simulation model in the current instance"""
        if close_other:
            self.close_model()

        logger.info("Creating a new model.")
        self._instance.NewModel()

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

    def reset_simulation(self, eventcontroller_object: str = None) -> None:
        """
        Resets the simulation

        Attributes:
        ----------
        eventcontroller_object : str, optional
            path to the Event Controller object to be reset. If not given, it defaults to the default event controller path (default: None)
        """
        self._instance.ResetSimulation(eventcontroller_object)

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
        self._instance.SaveModel(full_path)

    def start_simulation(self, eventcontroller_object: str = None) -> None:
        """
        Starts the simulation

        Attributes:
        ----------
        eventcontroller_object : str, optional
            path to the Event Controller object to be reset. If not given, it defaults to the default event controller path (default: None)
        """
        self._instance.StartSimulation(eventcontroller_object)

    def stop_simulation(self, eventcontroller_object: str = None) -> None:
        """
        Stops the simulation

        Attributes:
        ----------
        eventcontroller_object : str, optional
            path to the Event Controller object to be reset. If not given, it defaults to the default event controller path (default: None)
        """
        self._instance.StopSimulation(eventcontroller_object)
