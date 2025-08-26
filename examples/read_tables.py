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

        no_index = plantsim.get_table(".Models.Model.DataTableNoIndex")
        col_index = plantsim.get_table(".Models.Model.DataTableColIndex")
        row_index = plantsim.get_table(".Models.Model.DataTableRowIndex")
        both_index = plantsim.get_table(".Models.Model.DataTableBothIndex")

        print(no_index)
        print(col_index)
        print(row_index)
        print(both_index)

        plantsim.set_table(".Models.Model.DataTableNoIndex", no_index)
        plantsim.set_table(".Models.Model.DataTableColIndex", col_index)
        plantsim.set_table(".Models.Model.DataTableRowIndex", row_index)
        plantsim.set_table(".Models.Model.DataTableBothIndex", both_index)


if __name__ == "__main__":
    run_model()
