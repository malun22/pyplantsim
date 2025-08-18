import os
from pyplantsim import SimulationException, Plantsim, PlantsimLicense, PlantsimVersion

def run_model():
    with Plantsim(license=PlantsimLicense.RESEARCH, version=PlantsimVersion.V_MJ_25_MI_4,
                             visible=True, trusted=True, suppress_3d=False, show_msg_box=False) as plantsim:
        model_path = os.path.join(os.path.dirname(__file__), "testModel.spp")
        plantsim.load_model(model_path)

        plantsim.set_model(path=".Models.Model", set_event_controller=True, install_error_handler=True)
        try:
            plantsim.run_simulation(without_animation=False)
        except SimulationException:
            print("Simulation threw an Error")
            return

        value = plantsim.get_value('.Models.Model.DataTable["Amount",1]')

        print("The result is: ", value)


if __name__ == "__main__":
    run_model()
