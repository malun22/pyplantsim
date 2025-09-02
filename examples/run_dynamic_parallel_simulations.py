import os
from pyplantsim import (
    Plantsim,
    PlantsimLicense,
    PlantsimVersion,
    SimulationException,
)
from pyplantsim.instance_handler import SimulationJob, DynamicInstanceHandler
from functools import partial


def on_init(instance: Plantsim, additional_parameter: str):
    print(additional_parameter)
    network_path = ".Models.Model"
    if instance.network_path != network_path:
        model_path = os.path.join(os.path.dirname(__file__), "testModel.spp")
        instance.load_model(model_path)
        instance.set_network(
            path=network_path, set_event_controller=True, install_error_handler=True
        )

    instance.reset_simulation()


def on_endsim(instance: Plantsim):
    value = instance.get_value('.Models.Model.DataTable["Amount",1]')

    print("The result is: ", value)


def on_error(instance: Plantsim, error: SimulationException):
    print(error)


def main():
    with DynamicInstanceHandler(
        max_cpu=0.7,
        max_memory=0.7,
        max_instances=12,
        min_instances=1,
        license=PlantsimLicense.RESEARCH,
        version=PlantsimVersion.V_MJ_25_MI_4,
        visible=True,
        trusted=True,
        suppress_3d=False,
        show_msg_box=False,
    ) as handler:
        jobs = []
        for _ in range(1000):
            job = handler.queue_job(
                SimulationJob(
                    without_animation=True,
                    on_init=partial(on_init, additional_parameter="Plantsim Rocks!"),
                    on_endsim=on_endsim,
                    on_simulation_error=on_error,
                )
            )

            jobs.append(job)

        for job in jobs:
            handler.wait_for(job)
        # Alternative: handler.wait_all()


if __name__ == "__main__":
    main()
