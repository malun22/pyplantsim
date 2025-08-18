import pyplantsim


def create_model():
    with pyplantsim.Plantsim(
        license=pyplantsim.PlantsimLicense.STUDENT,
        version=pyplantsim.PlantsimVersion.V_MJ_22_MI_1,
        visible=True,
        trusted=True,
        suppress_3d=False,
        show_msg_box=False,
    ) as plantsim:
        plantsim.new_model()

        plantsim.save_model(
            folder_path=r"S:\Coding\Projects\pyplantsim", file_name="MyNewModel"
        )


if __name__ == "__main__":
    create_model()
