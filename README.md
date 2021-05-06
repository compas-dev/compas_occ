# COMPAS OCC

COMPAS wrapper for the Python bindings of OCC

**This package is in early stages of development!**

----

## Installation

```bash
conda create -n occ python=3.8 compas compas_view2 pythonocc-core
conda activate occ
pip install -e .
```

## Scripts

Initial API exploration scripts are available in `scripts`.

* `box_explorer1.py`
* `box_explorer2.py`
* `box_to_mesh1.py`
* `compas_to_occ_box.py`
* `compas_to_occ_tubemesh.py`
