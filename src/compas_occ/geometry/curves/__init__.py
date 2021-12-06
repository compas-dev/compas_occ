from .nurbs import OCCNurbsCurve

try:
    from compas.geometry import NurbsCurve
except ImportError:
    pass
else:
    from compas.plugins import plugin

    @plugin(category='factories', requires=['compas_occ'])
    def new_nurbscurve(cls, *args, **kwargs):
        # for _, value in inspect.getmembers(OCCNurbsCurve):
        #     if inspect.isfunction(value):
        #         if hasattr(value, '__isabstractmethod__'):
        #             raise Exception('Abstract method not implemented: {}'.format(value))

        return super(NurbsCurve, OCCNurbsCurve).__new__(OCCNurbsCurve)

    @plugin(category='factories', requires=['compas_occ'])
    def new_nurbscurve_from_parameters(*args, **kwargs):
        return OCCNurbsCurve.from_parameters(*args, **kwargs)

    @plugin(category='factories', requires=['compas_occ'])
    def new_nurbscurve_from_points(*args, **kwargs):
        return OCCNurbsCurve.from_points(*args, **kwargs)

    @plugin(category='factories', requires=['compas_occ'])
    def new_nurbscurve_from_interpolation(*args, **kwargs):
        return OCCNurbsCurve.from_interpolation(*args, **kwargs)

    @plugin(category='factories', requires=['compas_occ'])
    def new_nurbscurve_from_step(*args, **kwargs):
        return OCCNurbsCurve.from_step(*args, **kwargs)
