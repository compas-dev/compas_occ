from compas.plugins import plugin
from compas.geometry import NurbsSurface

from .nurbs import OCCNurbsSurface


@plugin(category='factories', requires=['compas_occ'])
def new_nurbssurface(cls, *args, **kwargs):
    return super(NurbsSurface, OCCNurbsSurface).__new__(OCCNurbsSurface)


@plugin(category='factories', requires=['compas_occ'])
def new_nurbssurface_from_parameters(*args, **kwargs):
    return OCCNurbsSurface.from_parameters(*args, **kwargs)


@plugin(category='factories', requires=['compas_occ'])
def new_nurbssurface_from_points(*args, **kwargs):
    return OCCNurbsSurface.from_points(*args, **kwargs)


@plugin(category='factories', requires=['compas_occ'])
def new_nurbssurface_from_fill(cls, *args, **kwargs):
    return OCCNurbsSurface.from_fill(*args, **kwargs)


@plugin(category='factories', requires=['compas_occ'])
def new_nurbssurface_from_step(cls, *args, **kwargs):
    return OCCNurbsSurface.from_step(*args, **kwargs)

