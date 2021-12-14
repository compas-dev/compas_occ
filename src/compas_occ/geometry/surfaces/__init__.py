from .nurbs import OCCNurbsSurface

try:
    from compas.geometry import NurbsSurface
except ImportError:
    pass
else:
    from compas.plugins import plugin

    @plugin(category='factories', requires=['compas_occ'])
    def new_nurbssurface(*args, **kwargs):
        return super(NurbsSurface, OCCNurbsSurface).__new__(OCCNurbsSurface)

    @plugin(category='factories', requires=['compas_occ'])
    def new_nurbssurface_from_parameters(*args, **kwargs):
        return OCCNurbsSurface.from_parameters(*args, **kwargs)

    @plugin(category='factories', requires=['compas_occ'])
    def new_nurbssurface_from_points(*args, **kwargs):
        return OCCNurbsSurface.from_points(*args, **kwargs)

    @plugin(category='factories', requires=['compas_occ'])
    def new_nurbssurface_from_fill(*args, **kwargs):
        return OCCNurbsSurface.from_fill(*args, **kwargs)

    @plugin(category='factories', requires=['compas_occ'])
    def new_nurbssurface_from_step(*args, **kwargs):
        return OCCNurbsSurface.from_step(*args, **kwargs)
