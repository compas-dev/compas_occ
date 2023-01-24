"""
********************************************************************************
compas_occ.brep
********************************************************************************

.. currentmodule:: compas_occ.brep

Classes
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    BRep
    BRepVertex
    BRepEdge
    BRepLoop
    BRepFace

"""
from compas.plugins import plugin

from .brepvertex import BRepVertex  # noqa: F401
from .brepedge import BRepEdge  # noqa: F401
from .breploop import BRepLoop  # noqa: F401
from .brepface import BRepFace  # noqa: F401
from .brep import BRep  # noqa: F401

@plugin(category="factories", requires=["OCC"])
def new_brep(*args, **kwargs):
    return object.__new__(BRep)


@plugin(category="factories", requires=["OCC"])
def from_brep(*args, **kwargs):
    return BRep.from_native(*args, **kwargs)


@plugin(category="factories", requires=["OCC"])
def from_box(*args, **kwargs):
    return BRep.from_box(*args, **kwargs)


@plugin(category="factories", requires=["OCC"])
def from_sphere(*args, **kwargs):
    return BRep.from_sphere(*args, **kwargs)

@plugin(category="factories", requires=["OCC"])
def from_cylinder(*args, **kwargs):
    return BRep.from_cylinder(*args, **kwargs)
