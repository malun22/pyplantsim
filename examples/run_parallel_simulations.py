import os
from pyplantsim import InstanceHandler, Plantsim, SimulationException
from functools import partial


def on_init(instance: Plantsim, additional_parameter: str):
    print(additional_parameter)
    model_path = os.path.join(os.path.dirname(__file__), "testModel.spp")
    if not instance.model_loaded:
        instance.load_model(model_path)
        instance.set_model(
            path=".Models.Model", set_event_controller=True, install_error_handler=True
        )


def on_endsim(instance: Plantsim):
    print("Simulation beendet in Instanz", instance)

    value = instance.get_value('.Models.Model.DataTable["Amount",1]')

    print("The result is: ", value)

    instance.reset_simulation()


def on_sim_error(instance, ex: SimulationException):
    print("Fehler in Instanz:", instance, "Exception:", ex)


def main():
    with InstanceHandler() as handler:
        handler.create_workers(2)
        for _ in range(10):
            handler.run_simulation(
                without_animation=True,
                on_init=partial(on_init, additional_parameter="Plantsim Rocks!"),
                on_endsim=on_endsim,
                on_simulation_error=on_sim_error,
            )
        handler.wait_all()


if __name__ == "__main__":
    main()
