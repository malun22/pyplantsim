import pyplantsim
import os


def run_model():
    instance_handler = InstanceHandler(amount_instances=4, license=pyplantsim.PlantsimLicense.RESEARCH, version="25.4",
                             visible=True, trusted=True, suppress_3d=False, show_msg_box=False)
    
    model_path = os.path.join(os.path.dirname(__file__), "testModel.spp")
    instance_handler.load_model(model_path)
    instance_handler = set_model(path=".Models.Model", set_event_controller=True)
    instance_handler.run_simulations(without_animation=True)

    values = instance_handler.get_value('.Models.Model.DataTable["Amount",1]')
    print(values)


if __name__ == "__main__":
    run_model()
