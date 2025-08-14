import pyplantsim
import time


def run_model():
    with pyplantsim.Plantsim(license=pyplantsim.PlantsimLicense.RESEARCH, version="25.4",
                             visible=True, trusted=True, suppress_3d=False, show_msg_box=False) as plantsim:

        plantsim.load_model(r"C:\Users\lbernsti\Documents\Projekte\Standardbibliothek\pyplantsim\examples\testModel.spp")

        plantsim.set_eventcontroller(".Models.Model.EventController")
        plantsim.start_simulation()

        while plantsim.is_simulation_running():
            time.sleep(1)


if __name__ == "__main__":
    run_model()
