from compas.plugins import plugin
from compas.geometry import Brep  # noqa: F401

from .brepvertex import OCCBrepVertex  # noqa: F401
from .brepedge import OCCBrepEdge  # noqa: F401
from .breploop import OCCBrepLoop  # noqa: F401
from .brepface import OCCBrepFace  # noqa: F401
from .brep import OCCBrep  # noqa: F401


@plugin(category="factories", requires=["compas_occ"])
def from_boolean_difference(*args, **kwargs):
    return OCCBrep.from_boolean_difference(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def from_boolean_intersection(*args, **kwargs):
    return OCCBrep.from_boolean_intersection(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def from_boolean_union(*args, **kwargs):
    return OCCBrep.from_boolean_union(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def from_box(*args, **kwargs):
    return OCCBrep.from_box(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def from_brepfaces(*args, **kwargs):
    return OCCBrep.from_brepfaces(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def from_cone(*args, **kwargs):
    return OCCBrep.from_cone(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def from_curves(*args, **kwargs):
    return OCCBrep.from_curves(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def from_cylinder(*args, **kwargs):
    return OCCBrep.from_cylinder(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def from_extrusion(*args, **kwargs):
    return OCCBrep.from_extrusion(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def from_iges(*args, **kwargs):
    return OCCBrep.from_iges(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def from_mesh(*args, **kwargs):
    return OCCBrep.from_mesh(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def from_native(*args, **kwargs):
    return OCCBrep.from_native(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def from_plane(*args, **kwargs):
    return OCCBrep.from_plane(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def from_planes(*args, **kwargs):
    return OCCBrep.from_planes(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def from_polygons(*args, **kwargs):
    return OCCBrep.from_polygons(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def from_sphere(*args, **kwargs):
    return OCCBrep.from_sphere(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def from_step(*args, **kwargs):
    return OCCBrep.from_step(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def from_surface(*args, **kwargs):
    return OCCBrep.from_surface(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def from_sweep(*args, **kwargs):
    return OCCBrep.from_sweep(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def from_torus(*args, **kwargs):
    return OCCBrep.from_torus(*args, **kwargs)


@plugin(category="factories", requires=["compas_occ"])
def new_brep(cls, *args, **kwargs):
    return super(Brep, cls).__new__(OCCBrep)
