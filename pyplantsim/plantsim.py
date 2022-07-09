from genericpath import exists
import os
import logging
import win32com.client

from pyplantsim.versions import PlantsimVersion
from pyplantsim.licenses import PlantsimLicense


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
    dispatch_id: str = "Tecnomatix.PlantSimulationRemoteControl"
    instance_running = False

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
        self.version: PlantsimVersion = version
        self.visible: bool = visible
        self.trusted: bool = trusted
        self.license: PlantsimLicense = license
        self.supress_3d = supress_3d
        self.show_msg_box = show_msg_box
        self.relative_path = relative_path

        self.instance_running: bool = False

        logging.info(
            f"Initializing Siemens Tecnomatix Plant Simulation {version.value} instance.")

        # Changing dispatch_id regarding requested version
        if version:
            self.dispatch_id += f"{self.dispatch_id}.{version.value}"

        self.instance = win32com.client.Dispatch(self.dispatch_id)

        # Should the instance window be visible on screen
        self.instance.SetVisible(self.visible)

        # Should the instance have access to the computer or not
        self.instance.SetTrustModels(self.trusted)

        # Set license
        self.instance.SetLicenseType(self.license.value)

        # Should the instance supress the start of 3D
        self.instance.SetSupressStartOf3D(self.supress_3d)

        # Should the instance show a message box
        self.instance.SetNoMessageBox(self.show_msg_box)

        # Set the start of relative paths
        self.instance.SetPathContext(self.relative_path)

        # Init was succesful
        self.instance_running = True

    def quit(self) -> None:
        """Quits the current instance."""
        if not self.instance_running:
            ...

        self.instance_running = False

        logging.info(
            "Closing Siemens Tecnomatix Plant Simulation {version.value} instance.")

        self.instance.Quit()

    def close_model(self) -> None:
        """Closes the active model"""
        self.instance.CloseModel()

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
