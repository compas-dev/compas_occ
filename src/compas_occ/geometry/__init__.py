"""
********************************************************************************
compas_occ.geometry
********************************************************************************

.. currentmodule:: compas_occ.geometry

Classes
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    OCCCurve
    OCCNurbsCurve
    OCCSurface
    OCCExtrusionSurface
    OCCRevolutionSurface
    OCCNurbsSurface

"""
from .curves import OCCCurve  # noqa: F401
from .curves import OCCNurbsCurve  # noqa: F401

from .surfaces import OCCSurface  # noqa: F401
from .surfaces import OCCExtrusionSurface  # noqa: F401
from .surfaces import OCCRevolutionSurface  # noqa: F401
from .surfaces import OCCNurbsSurface  # noqa: F401
