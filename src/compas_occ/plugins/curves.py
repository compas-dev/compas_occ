"""Curve plugin registrations for COMPAS."""

from collections.abc import Sequence
from typing import TYPE_CHECKING
from typing import cast

from compas.geometry._typing import TransformationType
from compas.geometry.curves.curve import CurveType
from compas.plugins import plugin
from compas.typing import FilePath
from compas.typing import PointLike

if TYPE_CHECKING:
    from compas.geometry import NurbsCurve
    from compas.geometry import Point
    from compas.geometry import Vector


@plugin(category="factories", requires=["OCC"])
def curve_from_native(cls: type[CurveType], *args: object, **kwargs: object) -> CurveType:
    from compas_occ.geometry import OCCCurve

    return cast(CurveType, OCCCurve.from_native(*args, **kwargs))


def _occ(curve):
    from compas_occ.geometry import OCCNurbsCurve

    return OCCNurbsCurve.from_native(curve.native_curve)


def _wrap(curve):
    from compas.geometry import NurbsCurve

    return NurbsCurve(native_curve=curve.native_curve)


def _new(method, *args, **kwargs):
    from compas_occ.geometry import OCCNurbsCurve

    return _wrap(getattr(OCCNurbsCurve, method)(*args, **kwargs))


@plugin(category="nurbscurve-factories", requires=["OCC"])
def from_native(native_curve: object) -> "NurbsCurve":
    return _new("from_native", native_curve)


@plugin(category="nurbscurve-factories", requires=["OCC"])
def from_interpolation(points: Sequence[PointLike], precision: float = 1e-3) -> "NurbsCurve":
    return _new("from_interpolation", points, precision=precision)


@plugin(category="nurbscurve-factories", requires=["OCC"])
def from_parameters(
    points: Sequence[PointLike],
    weights: Sequence[float],
    knots: Sequence[float],
    multiplicities: Sequence[int],
    degree: int,
    is_periodic: bool = False,
) -> "NurbsCurve":
    return _new("from_parameters", points, weights, knots, multiplicities, degree, is_periodic=is_periodic)


@plugin(category="nurbscurve-factories", requires=["OCC"])
def from_points(points: Sequence[PointLike], degree: int = 3, is_periodic: bool = False) -> "NurbsCurve":
    return _new("from_points", points, degree=degree, is_periodic=is_periodic)


@plugin(category="nurbscurve-io", requires=["OCC"])
def from_step(filepath: FilePath) -> "NurbsCurve":
    from OCC.Core.BRep import BRep_Tool
    from OCC.Core.Geom import Geom_TrimmedCurve
    from OCC.Core.GeomConvert import geomconvert

    from compas.geometry import NurbsCurve
    from compas_occ.brep import OCCBrep

    brep = OCCBrep.from_step(filepath, solid=False)
    if not brep.edges:
        raise ValueError("The STEP file does not contain a curve.")
    curve, first, last = BRep_Tool.Curve(brep.edges[0].occ_edge)
    native_curve = geomconvert.CurveToBSplineCurve(Geom_TrimmedCurve(curve, first, last))
    return NurbsCurve(native_curve=native_curve)


@plugin(category="nurbscurve-queries", requires=["OCC"])
def curve_points(curve: "NurbsCurve") -> list["Point"]:
    return _occ(curve).points


@plugin(category="nurbscurve-queries", requires=["OCC"])
def curve_weights(curve: "NurbsCurve") -> list[float]:
    return _occ(curve).weights


@plugin(category="nurbscurve-queries", requires=["OCC"])
def curve_knots(curve: "NurbsCurve") -> list[float]:
    return _occ(curve).knots


@plugin(category="nurbscurve-queries", requires=["OCC"])
def curve_multiplicities(curve: "NurbsCurve") -> list[int]:
    return _occ(curve).multiplicities


@plugin(category="nurbscurve-queries", requires=["OCC"])
def curve_continuity(curve: "NurbsCurve") -> int:
    return _occ(curve).continuity


@plugin(category="nurbscurve-queries", requires=["OCC"])
def curve_degree(curve: "NurbsCurve") -> int:
    return _occ(curve).degree


@plugin(category="nurbscurve-queries", requires=["OCC"])
def curve_is_rational(curve: "NurbsCurve") -> bool:
    return _occ(curve).is_rational


@plugin(category="nurbscurve-queries", requires=["OCC"])
def curve_domain(curve: "NurbsCurve") -> tuple[float, float]:
    return _occ(curve).domain


@plugin(category="nurbscurve-queries", requires=["OCC"])
def curve_length(curve: "NurbsCurve") -> float:
    return _occ(curve).length


@plugin(category="nurbscurve-queries", requires=["OCC"])
def curve_is_closed(curve: "NurbsCurve") -> bool:
    return _occ(curve).is_closed


@plugin(category="nurbscurve-queries", requires=["OCC"])
def curve_is_periodic(curve: "NurbsCurve") -> bool:
    return _occ(curve).is_periodic


@plugin(category="nurbscurve-evaluation", requires=["OCC"])
def curve_point_at(curve: "NurbsCurve", t: float, world: bool = True) -> "Point":
    return _occ(curve).point_at(t)


@plugin(category="nurbscurve-evaluation", requires=["OCC"])
def curve_normal_at(curve: "NurbsCurve", t: float, world: bool = True) -> "Vector | None":
    occ_curve = _occ(curve)
    curvature = occ_curve.curvature_at(t)
    if not curvature.length:
        return None
    return occ_curve.frame_at(t).yaxis


@plugin(category="nurbscurve-evaluation", requires=["OCC"])
def curve_tangent_at(curve: "NurbsCurve", t: float, world: bool = True) -> "Vector":
    return _occ(curve).tangent_at(t)


@plugin(category="nurbscurve-evaluation", requires=["OCC"])
def curve_curvature_at(curve: "NurbsCurve", t: float) -> "Vector":
    return _occ(curve).curvature_at(t)


@plugin(category="nurbscurve-operations", requires=["OCC"])
def curve_transform(curve: "NurbsCurve", transformation: TransformationType) -> None:
    _occ(curve).transform(transformation)


@plugin(category="nurbscurve-operations", requires=["OCC"])
def curve_reverse(curve: "NurbsCurve") -> None:
    _occ(curve).reverse()


@plugin(category="nurbscurve-operations", requires=["OCC"])
def curve_closest_point(curve: "NurbsCurve", point: PointLike, return_parameter: bool = False) -> "Point | tuple[Point, float]":
    return _occ(curve).closest_point(point, return_parameter=return_parameter)


@plugin(category="nurbscurve-operations", requires=["OCC"])
def curve_divide_by_count(curve: "NurbsCurve", count: int, return_points: bool = False) -> "list[float] | tuple[list[float], list[Point]]":
    return _occ(curve).divide_by_count(count, return_points=return_points)


@plugin(category="nurbscurve-operations", requires=["OCC"])
def curve_divide_by_length(curve: "NurbsCurve", length: float, return_points: bool = False) -> "list[float] | tuple[list[float], list[Point]]":
    return _occ(curve).divide_by_length(length, return_points=return_points)


@plugin(category="nurbscurve-io", requires=["OCC"])
def curve_to_step(curve: "NurbsCurve", filepath: FilePath, schema: str = "AP203") -> None:
    _occ(curve).to_step(str(filepath), schema=schema)
