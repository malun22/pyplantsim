from enum import Enum


class PlantsimLicense(Enum):
    """
    Enum representing the available Plant Simulation license types.

    :cvar PROFESSIONAL: Professional license.
    :cvar STANDARD: Standard license.
    :cvar FOUNDATION: Foundation license.
    :cvar APPLICATION: Application license.
    :cvar RUNTIME: Runtime license.
    :cvar RESEARCH: Research license.
    :cvar EDUCATIONAL: Educational license.
    :cvar STUDENT: Student license.
    :cvar VIEWER: Viewer license.
    """

    PROFESSIONAL = "Professional"
    STANDARD = "Standard"
    FOUNDATION = "Foundation"
    APPLICATION = "Application"
    RUNTIME = "Runtime"
    RESEARCH = "Research"
    EDUCATIONAL = "Educational"
    STUDENT = "Student"
    VIEWER = "Viewer"
