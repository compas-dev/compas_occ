from .surface import OCCSurface
from .nurbs import OCCNurbsSurface

from compas.plugins import plugin


@plugin(category="factories", requires=["compas_occ"])
def surface_from_native(cls, *args, **kwargs):
    return OCCSurface.from_native(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def nurbssurface_from_extrusion(cls, *args, **kwargs):
    return OCCNurbsSurface.from_extrusion(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def nurbssurface_from_fill(cls, *args, **kwargs):
    return OCCNurbsSurface.from_fill(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def nurbssurface_from_interpolation(cls, *args, **kwargs):
    return OCCNurbsSurface.from_interpolation(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def nurbssurface_from_native(cls, *args, **kwargs):
    return OCCNurbsSurface.from_native(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def nurbssurface_from_parameters(cls, *args, **kwargs):
    return OCCNurbsSurface.from_parameters(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def nurbssurface_from_plane(cls, *args, **kwargs):
    return OCCNurbsSurface.from_plane(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def nurbssurface_from_points(cls, *args, **kwargs):
    return OCCNurbsSurface.from_points(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def nurbssurface_from_step(cls, *args, **kwargs):
    return OCCNurbsSurface.from_step(*args, **kwargs)
