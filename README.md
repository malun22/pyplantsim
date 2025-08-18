<h1 align="center">
pyplantsim
</h1>

<h4 align="center">A python wrapper for <a href="https://www.dex.siemens.com/plm/tecnomatix/plant-simulation" target="_blank">Siemens Tecnomatix Plant Simulation</a> COM Interface.</h4>

<p align="center">
  <a href="#setup">Setup</a> •
  <a href="#examples">Examples</a> •
  <a href="#further-documentation">Further documentation</a> •
  <a href="#notice">Notice</a>
</p>

<!-- - [Setup](#setup)
- [Examples](#examples)
- [Further documentation](#further-documentation)
- [Notice](#notice) -->

## Setup

Install via pip:

```
pip install pyplantsim
```

## Examples

```python
import pyplantsim

with Plantsim(license=PlantsimLicense.STUDENT, version=PlantsimVersion.V_MJ_22_MI_1,
                    visible=True, trusted=True, suppress_3d=False, show_msg_box=False) as plantsim:

        plantsim.new_model()

        plantsim.save_model(
            folder_path=r"C:\users\documents\plantsimmodels", file_name="MyNewModel")
```

There are further examples in the [example folder](https://github.com/malun22/pyplantsim/tree/main/examples).

## Further documentation

Here is the official [COM Interface documentation](https://docs.plm.automation.siemens.com/content/plant_sim_help/15.1/plant_sim_all_in_one_html/en_US/tecnomatix_plant_simulation_help/add_ins_reference_help/inter_process_communication_interfaces/com.html)

## Notice

This is a private project and still in progress. This is not associated to Siemens in any way.
