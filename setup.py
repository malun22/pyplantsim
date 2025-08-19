from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="pyplantsim",
    version="0.2.1",
    description="A Python wrapper for Siemens Tecnomatix Plant Simulation COM Interface",
    keywords=["plant", "siemens", "simulation", "COM"],
    url="https://github.com/malun22/pyplantsim",
    author="Luca Bernstiel",
    author_email="bernstiel@gmx.de",
    packages=find_packages(),
    license="MIT",
    install_requires=[
        "colorama>=0.4.6",
        "loguru>=0.7.3",
        "pywin32>=311; platform_system=='Windows'",
        "setuptools>=80.9.0",
        "win32_setctime>=1.2.0; platform_system=='Windows'",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    package_data={
        "pyplantsim": ["sim_talk_scripts/*.st"],
    },
)
