from .curve import Curve  # noqa : F401
from .nurbs import NurbsCurve

try:
    from compas.geometry import NurbsCurve as BaseNurbsCurve
except ImportError:
    pass
else:
    from compas.plugins import plugin

    @plugin(category='factories', requires=['compas_occ'])
    def new_nurbscurve(*args, **kwargs):
        return super(BaseNurbsCurve, NurbsCurve).__new__(NurbsCurve)

    @plugin(category='factories', requires=['compas_occ'])
    def new_nurbscurve_from_parameters(*args, **kwargs):
        return NurbsCurve.from_parameters(*args, **kwargs)

    @plugin(category='factories', requires=['compas_occ'])
    def new_nurbscurve_from_points(*args, **kwargs):
        return NurbsCurve.from_points(*args, **kwargs)

    @plugin(category='factories', requires=['compas_occ'])
    def new_nurbscurve_from_interpolation(*args, **kwargs):
        return NurbsCurve.from_interpolation(*args, **kwargs)

    @plugin(category='factories', requires=['compas_occ'])
    def new_nurbscurve_from_step(*args, **kwargs):
        return NurbsCurve.from_step(*args, **kwargs)
