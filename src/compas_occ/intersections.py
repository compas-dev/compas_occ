"""Intersection operations implemented with Open CASCADE."""

from typing import Optional

from OCC.Core import BRepAlgoAPI
from OCC.Core import BRepIntCurveSurface
from OCC.Core import Geom
from OCC.Core import GeomAbs
from OCC.Core import GeomAdaptor
from OCC.Core import GeomAPI
from OCC.Core import GeomConvert

from compas.geometry import IntersectionResult
from compas.geometry import Line
from compas.geometry import NurbsCurve
from compas.geometry import Plane
from compas.geometry import Point
from compas.tolerance import TOL
from compas_occ.brep import OCCBrep
from compas_occ.brep import OCCBrepEdge
from compas_occ.conversions import circle_to_compas
from compas_occ.conversions import ellipse_to_compas
from compas_occ.conversions import hyperbola_to_compas
from compas_occ.conversions import line_to_compas
from compas_occ.conversions import line_to_occ
from compas_occ.conversions import parabola_to_compas
from compas_occ.conversions import plane_to_occ
from compas_occ.conversions import point_to_compas
from compas_occ.geometry import OCCCurve
from compas_occ.geometry import OCCSurface


def intersection_line_surface(line: Line, surface, tol: Optional[float] = None) -> IntersectionResult:
    """Compute the intersection points of an infinite line and a surface."""
    native_surface = _native_surface(surface)
    algorithm = GeomAPI.GeomAPI_IntCS(Geom.Geom_Line(line_to_occ(line)), native_surface)
    return IntersectionResult(tuple(point_to_compas(algorithm.Point(index)) for index in range(1, algorithm.NbPoints() + 1)))


def intersection_plane_surface(plane: Plane, surface, tol: Optional[float] = None) -> IntersectionResult:
    """Compute the intersection curves of an infinite plane and a surface."""
    native_plane = Geom.Geom_Plane(plane_to_occ(plane))
    return _intersection_surfaces(native_plane, _native_surface(surface), tol)


def intersection_curve_surface(curve, surface, tol: Optional[float] = None) -> IntersectionResult:
    """Compute the intersection points of a curve and a surface."""
    algorithm = GeomAPI.GeomAPI_IntCS(_native_curve(curve), _native_surface(surface))
    return IntersectionResult(tuple(point_to_compas(algorithm.Point(index)) for index in range(1, algorithm.NbPoints() + 1)))


def intersection_surface_surface(surface_a, surface_b, tol: Optional[float] = None) -> IntersectionResult:
    """Compute the intersection curves of two surfaces."""
    return _intersection_surfaces(_native_surface(surface_a), _native_surface(surface_b), tol)


def intersection_line_brep(line: Line, brep, tol: Optional[float] = None) -> IntersectionResult:
    """Compute the intersection points of an infinite line and a BRep boundary."""
    tolerance = TOL.absolute if tol is None else tol
    algorithm = BRepIntCurveSurface.BRepIntCurveSurface_Inter()
    algorithm.Init(_native_brep(brep), line_to_occ(line), tolerance)
    return IntersectionResult(tuple(_intersector_points(algorithm, tolerance)))


def intersection_plane_brep(plane: Plane, brep, tol: Optional[float] = None) -> IntersectionResult:
    """Compute the intersection curves of an infinite plane and a BRep boundary."""
    algorithm = BRepAlgoAPI.BRepAlgoAPI_Section(_native_brep(brep), plane_to_occ(plane), False)
    algorithm.SetFuzzyValue(TOL.absolute if tol is None else tol)
    return _section_curves(algorithm)


def intersection_curve_brep(curve, brep, tol: Optional[float] = None) -> IntersectionResult:
    """Compute the intersection points of a curve and a BRep boundary."""
    tolerance = TOL.absolute if tol is None else tol
    algorithm = BRepIntCurveSurface.BRepIntCurveSurface_Inter()
    algorithm.Init(_native_brep(brep), GeomAdaptor.GeomAdaptor_Curve(_native_curve(curve)), tolerance)
    return IntersectionResult(tuple(_intersector_points(algorithm, tolerance)))


def intersection_surface_brep(surface, brep, tol: Optional[float] = None) -> IntersectionResult:
    """Compute the intersection curves of a surface and a BRep boundary."""
    algorithm = BRepAlgoAPI.BRepAlgoAPI_Section(_native_brep(brep), _native_surface(surface), False)
    algorithm.SetFuzzyValue(TOL.absolute if tol is None else tol)
    return _section_curves(algorithm)


def _intersection_surfaces(surface_a, surface_b, tolerance: Optional[float]) -> IntersectionResult:
    tolerance = TOL.absolute if tolerance is None else tolerance
    algorithm = GeomAPI.GeomAPI_IntSS(surface_a, surface_b, tolerance)
    if not algorithm.IsDone():
        return IntersectionResult()
    return IntersectionResult(tuple(_curve_from_native(algorithm.Line(index)) for index in range(1, algorithm.NbLines() + 1)))


def _section_curves(algorithm) -> IntersectionResult:
    algorithm.Build()
    if not algorithm.IsDone():
        return IntersectionResult()
    section = OCCBrep.from_native(algorithm.Shape())
    return IntersectionResult(tuple(_curve_from_edge(edge) for edge in section.edges))


def _intersector_points(algorithm, tolerance: float) -> list[Point]:
    points = []
    while algorithm.More():
        point = point_to_compas(algorithm.Pnt())
        if not any(TOL.is_allclose(point, other, rtol=0, atol=tolerance) for other in points):
            points.append(point)
        algorithm.Next()
    return points


def _native_brep(brep):
    if isinstance(brep, OCCBrep):
        return brep.occ_shape
    native_brep = getattr(brep, "native_brep", None)
    if native_brep is None:
        raise TypeError("The BRep should expose OCC geometry through native_brep.")
    return native_brep


def _native_curve(curve):
    if isinstance(curve, Line):
        return Geom.Geom_Line(line_to_occ(curve))
    if isinstance(curve, OCCCurve):
        return curve.native_curve
    native_curve = getattr(curve, "native_curve", None)
    if native_curve is None:
        raise TypeError("The curve should expose OCC geometry through native_curve.")
    return native_curve


def _native_surface(surface):
    if isinstance(surface, Plane):
        return Geom.Geom_Plane(plane_to_occ(surface))
    if isinstance(surface, OCCSurface):
        return surface.native_surface
    native_surface = getattr(surface, "native_surface", None)
    if native_surface is None:
        raise TypeError("The surface should expose OCC geometry through native_surface.")
    return native_surface


def _curve_from_edge(edge: OCCBrepEdge):
    return edge.curve


def _curve_from_native(curve):
    adaptor = GeomAdaptor.GeomAdaptor_Curve(curve)
    curve_type = adaptor.GetType()
    if curve_type == GeomAbs.GeomAbs_Line:
        return line_to_compas(adaptor.Line())
    if curve_type == GeomAbs.GeomAbs_Circle:
        return circle_to_compas(adaptor.Circle())
    if curve_type == GeomAbs.GeomAbs_Ellipse:
        return ellipse_to_compas(adaptor.Ellipse())
    if curve_type == GeomAbs.GeomAbs_Hyperbola:
        return hyperbola_to_compas(adaptor.Hyperbola())
    if curve_type == GeomAbs.GeomAbs_Parabola:
        return parabola_to_compas(adaptor.Parabola())
    native_curve = GeomConvert.geomconvert.CurveToBSplineCurve(curve)
    return NurbsCurve(native_curve=native_curve)


__all__ = [
    "intersection_curve_brep",
    "intersection_curve_surface",
    "intersection_line_brep",
    "intersection_line_surface",
    "intersection_plane_brep",
    "intersection_plane_surface",
    "intersection_surface_brep",
    "intersection_surface_surface",
]
