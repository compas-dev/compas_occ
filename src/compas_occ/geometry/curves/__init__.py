from .curve2d import OCCCurve2d  # noqa : F401
from .curve import OCCCurve  # noqa: F401
from .nurbs import OCCNurbsCurve

from compas.geometry import Curve
from compas.geometry import NurbsCurve

from compas.plugins import plugin


@plugin(category="factories", requires=["compas_occ"])
def new_curve(cls, *args, **kwargs):
    # curve = object.__new__(OCCCurve)
    # return curve
    return super(Curve, cls).__new__(cls)


@plugin(category="factories", requires=["compas_occ"])
def new_nurbscurve(cls, *args, **kwargs):
    # curve = object.__new__(OCCNurbsCurve)
    # return curve
    return super(NurbsCurve, cls).__new__(cls)


@plugin(category="factories", requires=["compas_occ"])
def new_nurbscurve_from_native(cls, *args, **kwargs):
    return OCCNurbsCurve.from_occ(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def new_nurbscurve_from_parameters(cls, *args, **kwargs):
    return OCCNurbsCurve.from_parameters(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def new_nurbscurve_from_points(cls, *args, **kwargs):
    return OCCNurbsCurve.from_points(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def new_nurbscurve_from_interpolation(cls, *args, **kwargs):
    return OCCNurbsCurve.from_interpolation(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def new_nurbscurve_from_step(cls, *args, **kwargs):
    return OCCNurbsCurve.from_step(*args, **kwargs)
