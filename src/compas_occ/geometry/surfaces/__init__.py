from .nurbs import NurbsSurface

try:
    from compas.geometry import NurbsSurface as BaseNurbsSurface
except ImportError:
    pass
else:
    from compas.plugins import plugin

    @plugin(category='factories', requires=['compas_occ'])
    def new_nurbssurface(*args, **kwargs):
        return super(BaseNurbsSurface, NurbsSurface).__new__(NurbsSurface)

    @plugin(category='factories', requires=['compas_occ'])
    def new_nurbssurface_from_parameters(*args, **kwargs):
        return NurbsSurface.from_parameters(*args, **kwargs)

    @plugin(category='factories', requires=['compas_occ'])
    def new_nurbssurface_from_points(*args, **kwargs):
        return NurbsSurface.from_points(*args, **kwargs)

    @plugin(category='factories', requires=['compas_occ'])
    def new_nurbssurface_from_fill(*args, **kwargs):
        return NurbsSurface.from_fill(*args, **kwargs)

    @plugin(category='factories', requires=['compas_occ'])
    def new_nurbssurface_from_step(*args, **kwargs):
        return NurbsSurface.from_step(*args, **kwargs)
