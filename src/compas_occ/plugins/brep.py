"""Brep plugin registrations for COMPAS."""

from compas.plugins import plugin


def _occ(brep):
    from compas_occ.brep import OCCBrep

    if isinstance(brep, OCCBrep):
        return brep
    return OCCBrep.from_native(brep.native_brep)


def _wrap(brep):
    from compas.geometry import Brep

    return Brep(native_brep=brep.native_brep)


def _factory(method, *args, **kwargs):
    from compas_occ.brep import OCCBrep

    return _wrap(getattr(OCCBrep, method)(*args, **kwargs))


def _occ_curves(curves):
    from compas_occ.geometry import OCCNurbsCurve

    return [curve if isinstance(curve, OCCNurbsCurve) else OCCNurbsCurve.from_native(curve.native_curve) for curve in curves]


def _occ_breps(value):
    if isinstance(value, (list, tuple)):
        return [_occ(item) for item in value]
    return _occ(value)


def _unique(items):
    unique = []
    for item in items:
        if not any(item.is_same(other) for other in unique):
            unique.append(item)
    return unique


def _register_factory(name):
    def factory(*args, **kwargs):
        return _factory(name, *args, **kwargs)

    factory.__name__ = name
    return plugin(category="brep-factories", requires=["OCC"])(factory)


from_box = _register_factory("from_box")
from_brepfaces = _register_factory("from_brepfaces")
from_cylinder = _register_factory("from_cylinder")
from_extrusion = _register_factory("from_extrusion")
from_mesh = _register_factory("from_mesh")
from_plane = _register_factory("from_plane")
from_planes = _register_factory("from_planes")
from_polygons = _register_factory("from_polygons")
from_sphere = _register_factory("from_sphere")
from_sweep = _register_factory("from_sweep")
from_torus = _register_factory("from_torus")


@plugin(category="brep-factories", requires=["OCC"])
def from_breps(breps, *args, **kwargs):
    return _factory("from_breps", [_occ(brep) for brep in breps], *args, **kwargs)


@plugin(category="brep-factories", requires=["OCC"])
def from_loft(curves, *args, **kwargs):
    return _factory("from_loft", _occ_curves(curves), *args, **kwargs)


@plugin(category="brep-factories", requires=["OCC"])
def from_native(native_brep):
    return _factory("from_native", native_brep)


@plugin(category="brep-io", requires=["OCC"])
def from_iges(*args, **kwargs):
    return _factory("from_iges", *args, **kwargs)


@plugin(category="brep-io", requires=["OCC"])
def from_step(*args, **kwargs):
    return _factory("from_step", *args, **kwargs)


@plugin(category="brep-operations", requires=["OCC"])
def from_boolean_difference(brep_a, brep_b):
    return _factory("from_boolean_difference", _occ_breps(brep_a), _occ_breps(brep_b))


@plugin(category="brep-operations", requires=["OCC"])
def from_boolean_intersection(brep_a, brep_b):
    return _factory("from_boolean_intersection", _occ_breps(brep_a), _occ_breps(brep_b))


@plugin(category="brep-operations", requires=["OCC"])
def from_boolean_union(brep_a, brep_b):
    return _factory("from_boolean_union", _occ_breps(brep_a), _occ_breps(brep_b))


@plugin(category="brep-serialization", requires=["OCC"])
def brep_to_data(brep):
    return _occ(brep).to_data(include_native=True)


@plugin(category="brep-serialization", requires=["OCC"])
def brep_rebuild(brep, data):
    from compas_occ.brep import OCCBrep

    rebuilt = OCCBrep.from_data(data)
    brep._native_brep = rebuilt.native_brep


@plugin(category="brep-queries", requires=["OCC"])
def brep_area(brep):
    return _occ(brep).area


@plugin(category="brep-queries", requires=["OCC"])
def brep_centroid(brep):
    return _occ(brep).centroid


@plugin(category="brep-queries", requires=["OCC"])
def brep_frame(brep):
    return _occ(brep).frame


@plugin(category="brep-queries", requires=["OCC"])
def brep_volume(brep):
    return _occ(brep).volume


@plugin(category="brep-queries", requires=["OCC"])
def brep_classification(brep):
    from OCC.Core.BRepCheck import BRepCheck_Analyzer
    from OCC.Core.TopAbs import TopAbs_FACE

    occ = _occ(brep)
    return {
        "orientation": int(occ.orientation),
        "type": int(occ.type),
        "is_valid": BRepCheck_Analyzer(occ.occ_shape).IsValid(),
        "is_orientable": occ.is_orientable,
        "is_closed": occ.is_closed,
        "is_infinite": occ.is_infinite,
        "is_convex": occ.is_convex,
        "is_manifold": occ.is_manifold,
        "is_surface": occ.type == TopAbs_FACE,
        "is_compound": occ.is_compound,
        "is_compoundsolid": occ.is_compoundsolid,
        "is_shell": occ.is_shell,
        "is_solid": occ.is_solid,
    }


@plugin(category="brep-queries", requires=["OCC"])
def brep_topology(brep):
    occ = _occ(brep)
    return {
        "vertices": _unique(occ.vertices),
        "edges": _unique(occ.edges),
        "trims": [],
        "loops": _unique(occ.loops),
        "faces": _unique(occ.faces),
        "shells": [_wrap(shell) for shell in occ.shells],
        "solids": [_wrap(solid) for solid in occ.solids],
    }


@plugin(category="brep-operations", requires=["OCC"])
def brep_tessellate(brep, linear_deflection=None, angular_deflection=None, **kwargs):
    from compas.geometry import Polyline

    tessellation = _occ(brep).compute_tessellation(linear_deflection, angular_deflection)
    polylines = [Polyline(points) for points in tessellation.polylines]
    return tessellation.to_mesh(), polylines


@plugin(category="brep-operations", requires=["OCC"])
def brep_fillet(brep, radius, exclude=None):
    return _wrap(_occ(brep).filleted(radius, exclude=exclude))


def _copy_and_apply(brep, method, *args, **kwargs):
    result = _occ(brep).copy()
    getattr(result, method)(*args, **kwargs)
    return _wrap(result)


@plugin(category="brep-operations", requires=["OCC"])
def brep_fix(brep):
    return _copy_and_apply(brep, "fix")


@plugin(category="brep-operations", requires=["OCC"])
def brep_flip(brep):
    result = _occ(brep).copy()
    result.occ_shape.Reverse()
    return _wrap(result)


@plugin(category="brep-operations", requires=["OCC"])
def brep_heal(brep):
    return _copy_and_apply(brep, "heal")


@plugin(category="brep-operations", requires=["OCC"])
def brep_make_solid(brep):
    return _copy_and_apply(brep, "make_solid")


@plugin(category="brep-operations", requires=["OCC"])
def brep_overlap(brep_a, brep_b, **kwargs):
    return _occ(brep_a).overlap(_occ(brep_b), **kwargs)


@plugin(category="brep-operations", requires=["OCC"])
def brep_sew(brep):
    return _copy_and_apply(brep, "sew")


@plugin(category="brep-operations", requires=["OCC"])
def brep_slice(brep, plane):
    result = _occ(brep).slice(plane)
    return _wrap(result) if result else None


@plugin(category="brep-operations", requires=["OCC"])
def brep_split(brep, cutter):
    return [_wrap(result) for result in _occ(brep).split(_occ(cutter))]


@plugin(category="brep-operations", requires=["OCC"])
def brep_trimmed(brep, plane):
    return _wrap(_occ(brep).trimmed(plane))


@plugin(category="brep-io", requires=["OCC"])
def brep_to_iges(brep, filepath):
    return _occ(brep).to_iges(filepath)


@plugin(category="brep-io", requires=["OCC"])
def brep_to_step(brep, filepath):
    _occ(brep).to_step(filepath)


@plugin(category="brep-io", requires=["OCC"])
def brep_to_stl(brep, filepath):
    return _occ(brep).to_stl(filepath)
