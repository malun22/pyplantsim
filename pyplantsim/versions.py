from enum import Enum


class PlantsimVersion(Enum):
    """
    Enum representing the available Plant Simulation version identifiers.

    :cvar V_MJ_25_MI_4: Version 25.4
    :cvar V_MJ_24_MI_4: Version 24.4
    :cvar V_MJ_23_MI_4: Version 23.2
    :cvar V_MJ_22_MI_1: Version 22.1
    :cvar V_MJ_22_MI_0: Version 22.0
    :cvar V_MJ_16_MI_0: Version 16.0
    """

    V_MJ_25_MI_4 = "25.4"
    V_MJ_24_MI_4 = "24.4"
    V_MJ_23_MI_4 = "23.2"
    V_MJ_22_MI_1 = "22.1"
    V_MJ_22_MI_0 = "22.0"
    V_MJ_16_MI_0 = "16.0"
