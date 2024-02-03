from .surface import OCCSurface  # noqa : F401
from .revolution import OCCRevolutionSurface  # noqa : F401
from .extrusion import OCCExtrusionSurface  # noqa : F401
from .nurbs import OCCNurbsSurface

from compas.geometry import Surface
from compas.geometry import NurbsSurface
from compas.plugins import plugin


@plugin(category="factories", requires=["compas_occ"])
def new_surface(cls, *args, **kwargs):
    return super(Surface, cls).__new__(cls)


@plugin(category="factories", requires=["compas_occ"])
def new_surface_from_plane(cls, *args, **kwargs):
    return OCCSurface.from_plane(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def new_nurbssurface(cls, *args, **kwargs):
    return super(NurbsSurface, cls).__new__(cls)


@plugin(category="factories", requires=["compas_occ"])
def new_nurbssurface_from_native(cls, *args, **kwargs):
    return OCCNurbsSurface.from_occ(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def new_nurbssurface_from_parameters(cls, *args, **kwargs):
    return OCCNurbsSurface.from_parameters(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def new_nurbssurface_from_points(cls, *args, **kwargs):
    return OCCNurbsSurface.from_points(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def new_nurbssurface_from_fill(cls, *args, **kwargs):
    return OCCNurbsSurface.from_fill(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def new_nurbssurface_from_step(cls, *args, **kwargs):
    return OCCNurbsSurface.from_step(*args, **kwargs)
