"""Surface plugin registrations for COMPAS."""

from collections.abc import Sequence
from typing import TYPE_CHECKING
from typing import cast

from compas.geometry.surfaces.nurbs_operations import ControlPointGrid
from compas.geometry.surfaces.nurbs_operations import WeightGrid
from compas.geometry.surfaces.surface import SurfaceType
from compas.plugins import plugin

if TYPE_CHECKING:
    from compas.geometry import NurbsSurface
    from compas.geometry import Plane


@plugin(category="factories", requires=["OCC"])
def surface_from_native(cls: type[SurfaceType], *args: object, **kwargs: object) -> SurfaceType:
    from compas_occ.geometry import OCCSurface

    return cast(SurfaceType, OCCSurface.from_native(*args, **kwargs))


def _occ(surface):
    from compas_occ.geometry import OCCNurbsSurface

    return OCCNurbsSurface.from_native(surface.native_surface)


def _wrap(surface):
    from compas.geometry import NurbsSurface

    return NurbsSurface(native_surface=surface.native_surface)


def _wrap_curve(curve):
    from compas.geometry import NurbsCurve

    return NurbsCurve(native_curve=curve.native_curve)


def _new(method, *args, **kwargs):
    from compas_occ.geometry import OCCNurbsSurface

    return _wrap(getattr(OCCNurbsSurface, method)(*args, **kwargs))


def _occ_curve(curve):
    from compas_occ.geometry import OCCNurbsCurve

    return OCCNurbsCurve.from_native(curve.native_curve)


@plugin(category="nurbssurface-factories", requires=["OCC"])
def from_extrusion(curve, vector):
    return _new("from_extrusion", _occ_curve(curve), vector)


@plugin(category="nurbssurface-factories", requires=["OCC"])
def from_fill(curve1, curve2, curve3=None, curve4=None, style="stretch"):
    curves = [_occ_curve(curve) if curve is not None else None for curve in (curve1, curve2, curve3, curve4)]
    return _new("from_fill", *curves, style=style)


@plugin(category="nurbssurface-factories", requires=["OCC"])
def from_interpolation(points: ControlPointGrid, precision: float = 1e-3) -> "NurbsSurface":
    return _new("from_interpolation", points, precision=precision)


@plugin(category="nurbssurface-factories", requires=["OCC"])
def from_frame(frame):
    from compas.geometry import Plane

    return _new("from_plane", Plane.from_frame(frame))


@plugin(category="nurbssurface-factories", requires=["OCC"])
def from_native(native_surface: object) -> "NurbsSurface":
    return _new("from_native", native_surface)


@plugin(category="nurbssurface-factories", requires=["OCC"])
def from_parameters(
    points: ControlPointGrid,
    weights: WeightGrid,
    knots_u: Sequence[float],
    knots_v: Sequence[float],
    mults_u: Sequence[int],
    mults_v: Sequence[int],
    degree_u: int,
    degree_v: int,
    is_periodic_u: bool = False,
    is_periodic_v: bool = False,
) -> "NurbsSurface":
    return _new(
        "from_parameters",
        points,
        weights,
        knots_u,
        knots_v,
        mults_u,
        mults_v,
        degree_u,
        degree_v,
        is_periodic_u=is_periodic_u,
        is_periodic_v=is_periodic_v,
    )


@plugin(category="nurbssurface-factories", requires=["OCC"])
def from_plane(plane: "Plane") -> "NurbsSurface":
    return _new("from_plane", plane)


@plugin(category="nurbssurface-factories", requires=["OCC"])
def from_points(points: ControlPointGrid, degree_u: int = 3, degree_v: int = 3) -> "NurbsSurface":
    return _new("from_points", points, degree_u=degree_u, degree_v=degree_v)


@plugin(category="nurbssurface-io", requires=["OCC"])
def from_step(filepath):
    from compas_occ.brep import OCCBrep

    brep = OCCBrep.from_step(filepath, solid=False)
    if not brep.faces:
        raise ValueError("The STEP file does not contain a surface.")
    return _wrap(brep.faces[0].nurbssurface)


@plugin(category="nurbssurface-queries", requires=["OCC"])
def surface_points(surface):
    return _occ(surface).points.points


@plugin(category="nurbssurface-queries", requires=["OCC"])
def surface_weights(surface):
    return _occ(surface).weights


@plugin(category="nurbssurface-queries", requires=["OCC"])
def surface_knots_u(surface):
    return _occ(surface).knots_u


@plugin(category="nurbssurface-queries", requires=["OCC"])
def surface_knots_v(surface):
    return _occ(surface).knots_v


@plugin(category="nurbssurface-queries", requires=["OCC"])
def surface_mults_u(surface):
    return _occ(surface).mults_u


@plugin(category="nurbssurface-queries", requires=["OCC"])
def surface_mults_v(surface):
    return _occ(surface).mults_v


@plugin(category="nurbssurface-queries", requires=["OCC"])
def surface_degree_u(surface):
    return _occ(surface).degree_u


@plugin(category="nurbssurface-queries", requires=["OCC"])
def surface_degree_v(surface):
    return _occ(surface).degree_v


@plugin(category="nurbssurface-queries", requires=["OCC"])
def surface_domain_u(surface):
    return _occ(surface).domain_u


@plugin(category="nurbssurface-queries", requires=["OCC"])
def surface_domain_v(surface):
    return _occ(surface).domain_v


@plugin(category="nurbssurface-queries", requires=["OCC"])
def surface_is_periodic_u(surface):
    return _occ(surface).is_periodic_u


@plugin(category="nurbssurface-queries", requires=["OCC"])
def surface_is_periodic_v(surface):
    return _occ(surface).is_periodic_v


@plugin(category="nurbssurface-evaluation", requires=["OCC"])
def surface_isocurve_u(surface, u):
    return _wrap_curve(_occ(surface).isocurve_u(u))


@plugin(category="nurbssurface-evaluation", requires=["OCC"])
def surface_isocurve_v(surface, v):
    return _wrap_curve(_occ(surface).isocurve_v(v))


@plugin(category="nurbssurface-evaluation", requires=["OCC"])
def surface_boundary(surface):
    return [_wrap_curve(curve) for curve in _occ(surface).boundary()]


@plugin(category="nurbssurface-evaluation", requires=["OCC"])
def surface_point_at(surface, u, v):
    return _occ(surface).point_at(u, v)


@plugin(category="nurbssurface-evaluation", requires=["OCC"])
def surface_normal_at(surface, u, v):
    return _occ(surface).normal_at(u, v)


@plugin(category="nurbssurface-evaluation", requires=["OCC"])
def surface_frame_at(surface, u, v):
    return _occ(surface).frame_at(u, v)


@plugin(category="nurbssurface-evaluation", requires=["OCC"])
def surface_closest_point(surface, point, return_parameters=False):
    return _occ(surface).closest_point(point, return_parameters=return_parameters)


@plugin(category="nurbssurface-operations", requires=["OCC"])
def surface_transform(surface, transformation):
    _occ(surface).transform(transformation)


@plugin(category="nurbssurface-operations", requires=["OCC"])
def surface_to_brep(surface):
    from compas_occ.brep import OCCBrep

    return OCCBrep.from_surface(_occ(surface))


@plugin(category="nurbssurface-io", requires=["OCC"])
def surface_to_step(surface, filepath, schema="AP203"):
    _occ(surface).to_step(str(filepath), schema=schema)
