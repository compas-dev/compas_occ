from .curve2d import OCCCurve2d  # noqa : F401
from .curve import OCCCurve
from .nurbs import OCCNurbsCurve

from compas.plugins import plugin


@plugin(category="factories", requires=["compas_occ"])
def curve_from_native(cls, *args, **kwargs):
    return OCCCurve.from_native(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def nurbscurve_from_native(cls, *args, **kwargs):
    return OCCNurbsCurve.from_native(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def nurbscurve_from_interpolation(cls, *args, **kwargs):
    return OCCNurbsCurve.from_interpolation(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def nurbscurve_from_parameters(cls, *args, **kwargs):
    return OCCNurbsCurve.from_parameters(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def nurbscurve_from_points(cls, *args, **kwargs):
    return OCCNurbsCurve.from_points(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def nurbscurve_from_step(cls, *args, **kwargs):
    return OCCNurbsCurve.from_step(*args, **kwargs)
