"""
********************************************************************************
compas_occ
********************************************************************************

.. currentmodule:: compas_occ


.. toctree::
    :maxdepth: 1

    compas_occ.brep
    compas_occ.conversions
    compas_occ.geometry

"""

from __future__ import print_function

import os


__author__ = ["tom van mele"]
__copyright__ = "Block Research Group - ETH Zurich"
__license__ = "MIT License"
__email__ = "van.mele@arch.ethz.ch"
__version__ = "0.3.4"


HERE = os.path.dirname(__file__)

HOME = os.path.abspath(os.path.join(HERE, "../../"))
DATA = os.path.abspath(os.path.join(HOME, "data"))
DOCS = os.path.abspath(os.path.join(HOME, "docs"))
TEMP = os.path.abspath(os.path.join(HOME, "temp"))


__all__ = ["HOME", "DATA", "DOCS", "TEMP"]

__all_plugins__ = [
    'compas_occ.geometry.curves',
    'compas_occ.geometry.surfaces',
]
