import os
import logging
import win32com.client

from pyplantsim.versions import PlantsimVersion
from pyplantsim.licenses import PlantsimLicense
from pyplantsim.errors import PlantsimErrors
from pyplantsim.path import PlantsimPath


class Plantsim:
    """
    A wrapper class for Siemens Tecnomatix Plant Simulation COM Interface

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
    supress_3d : bool
        whether the instance should supress the start of 3D (default False)
    show_msg_box : bool 
        whether the instance should show a message box (default False)
    relative_path : str
        the start of relative paths (default "")
    """

    # Defaults
    _dispatch_id: str = "Tecnomatix.PlantSimulationRemoteControl"
    _instance_running: bool = False
    _event_controller: str = None
    _visible: bool = None
    _trusted: bool = None
    _license: PlantsimLicense = None
    _supress_3d: bool = None
    _show_msg_box: bool = None
    _relative_path: str = None

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        if self.instance_running:
            self.quit()

    def __enter__(self) -> None:
        return self

    def __init__(self, version: PlantsimVersion = PlantsimVersion.V_MJ_22_MI_1, visible: bool = True, trusted: bool = True,
                 license: PlantsimLicense = PlantsimLicense.VIEWER, supress_3d: bool = False, show_msg_box: bool = False, relative_path: str = "") -> None:
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
        supress_3d : bool
            whether the instance should supress the start of 3D (default False)
        show_msg_box : bool 
            whether the instance should show a message box (default False)
        relative_path : str
            the start of relative paths (default "")
        """

        # Inits
        self._version: PlantsimVersion = version

        self._instance_running: bool = False

        logging.info(
            f"Initializing Siemens Tecnomatix Plant Simulation {self._version.value} instance.")

        # Changing dispatch_id regarding requested version
        if self._version:
            self._dispatch_id += f".{self._version.value}"

        self.instance = win32com.client.Dispatch(self._dispatch_id)

        # Should the instance window be visible on screen
        self.set_visible(visible)

        # Should the instance have access to the computer or not
        self.set_trust_models(trusted)

        # Set license
        self.set_license(license)

        # Should the instance supress the start of 3D
        self.set_supress_start_of_3d(supress_3d)

        # Should the instance show a message box
        self.set_show_message_box(show_msg_box)

        # Init was succesful
        self._instance_running = True

    def set_path_context(self, path: PlantsimPath) -> None:
        """Sets the relative path. (For instance .Models.Model)"""
        if self._relative_path != path:
            self._relative_path != path
            self.instance.SetPathContext(str(self._relative_path))

    def set_show_message_box(self, show: bool) -> None:
        """Should the instance show a message box"""
        if self._show_msg_box != show:
            self._show_msg_box = show
            self.instance.SetNoMessageBox(self._show_msg_box)

    def set_supress_start_of_3d(self, supress: bool) -> None:
        """Should the instance supress the start of 3D"""
        if self._supress_3d != supress:
            self._supress_3d = supress
            self.instance.SetSupressStartOf3D(self._supress_3d)

    def set_license(self, license: PlantsimLicense) -> None:
        """Sets the license for the instance"""
        if self._license != license:
            self._license = license
            self.instance.SetLicenseType(self._license.value)

    def set_visible(self, visible: bool) -> None:
        """Should the instance window be visible on screen"""
        if self._visible != visible:
            self._visible = visible
            self.instance.SetVisible(self._visible)

    def set_trust_models(self, trusted: bool) -> None:
        """Should the instance have access to the computer or not"""
        if self._trusted != trusted:
            self._trusted = trusted
            self.instance.SetTrustModels(self._trusted)

    def quit(self) -> None:
        """Quits the current instance."""
        if not self._instance_running:
            ...

        self._instance_running = False

        logging.info(
            "Closing Siemens Tecnomatix Plant Simulation {version.value} instance.")

        self.instance.Quit()

    def close_model(self) -> None:
        """Closes the active model"""
        self.instance.CloseModel()

    def set_eventcontroller(self, path: str = None) -> None:
        """
        Sets the path of the Event Controller

        Attributes:
        ----------
        path : str, optional
            Path to the EventController object. If not give, it defaults to the defaul relative paths EventController (default: None)
        """
        if path:
            self._event_controller = path
        elif self._relative_path:
            self._event_controller = str(PlantsimPath(
                self._relative_path, "EventController"))

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
        return self.instance.ExecuteSimTalk(source_code, parameters)

    def get_value(self, object_name: str) -> any:
        """
        returns the value of an attribute of a Plant Simulation object
        """
        return self.instance.GetValue(object_name)

    @property
    def is_simulation_running(self) -> bool:
        """
        Property holding true, when the simulation is running at the moment, false, when it is not running
        """
        return self.instance.IsSimulationRunning()

    def load_model(self, filepath: str, password: str = None) -> None:
        """
        Loading a model into the current instance

        Attributes:
        ----------
        filepath : str
            The full path to the model file (.spp) 
        password : str, optional
            designates the password that is used for loading an encrypted model (default is None)
        """
        if not os.path.exists(filepath):
            ...  # Raise error

        logging.info(f"Loading {filepath}.")

        if password:
            self.instance.LoadModel(filepath, password)
        else:
            self.instance.LoadModel(filepath)

    def new_model(self) -> None:
        """Creates a new simulation model in the current instance"""
        self.instance.NewModel()

    def open_console_log_file(self, filepath: str) -> None:
        """Routes the Console output to a file"""
        self.instance.OpenConsoleLogFile(filepath)

    def close_console_log_file(self) -> None:
        """Closes the routing to the output file"""
        self.instance.OpenConsoleLogFile("")

    def quit_after_time(self, time: int) -> None:
        """
        Quits the current instance after a specified time

        Attributes:
        ----------
        time : int
            time after the instrance quits in seconds   
        """
        self.instance.QuitAfterTime(time)

    def reset_simulation(self, eventcontroller_object: str = None) -> None:
        """
        Resets the simulation

        Attributes:
        ----------
        eventcontroller_object : str, optional
            path to the Event Controller object to be reset. If not given, it defaults to the default event controller path (default: None)
        """
        self.instance.ResetSimulation(eventcontroller_object)

    def save_model(self, name: str) -> None:
        """Saves the current model as the given name"""
        self.instance.SaveModel(name)

    def set_value(self, object: str, value: any) -> None:
        """
        Sets a value to an given attribute

        Attributes:
        ----------
        object : str
            path to the attribute
        value : any
            the new value the attribute should be assigned to
        """
        self.instance.SetValue(object, value)

    def start_simulation(self, eventcontroller_object: str = None) -> None:
        """
        Starts the simulation

        Attributes:
        ----------
        eventcontroller_object : str, optional
            path to the Event Controller object to be reset. If not given, it defaults to the default event controller path (default: None)
        """
        self.instance.StartSimulation(eventcontroller_object)

    def stop_simulation(self, eventcontroller_object: str = None) -> None:
        """
        Stops the simulation

        Attributes:
        ----------
        eventcontroller_object : str, optional
            path to the Event Controller object to be reset. If not given, it defaults to the default event controller path (default: None)
        """
        self.instance.StopSimulation(eventcontroller_object)
