import pyplantsim
import time
import os


def run_model():
    with pyplantsim.Plantsim(license=pyplantsim.PlantsimLicense.RESEARCH, version="25.4",
                             visible=True, trusted=True, suppress_3d=False, show_msg_box=False) as plantsim:
        model_path = os.path.join(os.path.dirname(__file__), "testModel.spp")
        plantsim.load_model(model_path)

        plantsim.set_event_controller(".Models.Model.EventController")
        plantsim.start_simulation()

        while plantsim.is_simulation_running():
            time.sleep(1)

        value = plantsim.get_value_by_path('.Models.Model.DataTable["Amount",1]')

        print(value)


if __name__ == "__main__":
    run_model()
