import pyplantsim
import os


def run_model():
    with pyplantsim.Plantsim(license=pyplantsim.PlantsimLicense.RESEARCH, version="25.4",
                             visible=True, trusted=True, suppress_3d=False, show_msg_box=False) as plantsim:
        model_path = os.path.join(os.path.dirname(__file__), "testModel.spp")
        plantsim.load_model(model_path)

        plantsim.set_model(path=".Models.Model", set_event_controller=True)
        plantsim.run_simulation(without_animation=True)

        value = plantsim.get_value('.Models.Model.DataTable["Amount",1]')

        print(value)


if __name__ == "__main__":
    run_model()
