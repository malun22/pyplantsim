import os
from pyplantsim import Plantsim, PlantsimLicense, PlantsimVersion


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

        plantsim.set_network(
            path=".Models.Model", set_event_controller=True, install_error_handler=True
        )

        call_cycles = plantsim.get_call_cycles()

        print(call_cycles)


if __name__ == "__main__":
    run_model()
