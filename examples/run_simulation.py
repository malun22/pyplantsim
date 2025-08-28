import os
from pyplantsim import SimulationException, Plantsim, PlantsimLicense, PlantsimVersion


def on_progress(
    instance: Plantsim, progress: float
): ...  # Here a progressbar could be created


def run_model():
    with Plantsim(
        license=PlantsimLicense.RESEARCH,
        version=PlantsimVersion.V_MJ_25_MI_4,
        visible=True,
        trusted=True,
        suppress_3d=False,
        show_msg_box=False,
    ) as plantsim:
        model_path = os.path.join(os.path.dirname(__file__), "testModel.spp")
        plantsim.load_model(model_path)

        if not plantsim.exists_path(".Models.Model"):
            print("Model not found")
            return

        plantsim.set_network(
            path=".Models.Model", set_event_controller=True, install_error_handler=True
        )

        start_date = plantsim.get_start_date()
        print("Start Date is: ", start_date)

        try:
            plantsim.run_simulation(without_animation=False, on_progress=on_progress)
        except SimulationException:
            print("Simulation threw an Error")
            return

        plantsim.remove_error_handler()

        value = plantsim.get_value('.Models.Model.DataTable["Amount",1]')

        print("The result is: ", value)


if __name__ == "__main__":
    run_model()
