from .surface import OCCSurface  # noqa : F401
from .revolution import OCCRevolutionSurface  # noqa : F401
from .extrusion import OCCExtrusionSurface  # noqa : F401
from .nurbs import OCCNurbsSurface

try:
    from compas.geometry import Surface
    from compas.geometry import NurbsSurface
except ImportError:
    pass
else:
    from compas.plugins import plugin

    @plugin(category="factories", requires=["compas_occ"])
    def new_surface(cls, *args, **kwargs):
        return super(Surface, cls).__new__(cls)

    @plugin(category="factories", requires=["compas_occ"])
    def new_nurbssurface(cls, *args, **kwargs):
        return super(NurbsSurface, cls).__new__(cls)

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
