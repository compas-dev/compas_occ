"""Intersection plugin registrations for COMPAS."""

from typing import TYPE_CHECKING
from typing import Any

from compas.plugins import plugin

if TYPE_CHECKING:
    from compas.geometry import Brep
    from compas.geometry import Curve
    from compas.geometry import IntersectionResult
    from compas.geometry import Line
    from compas.geometry import Plane
    from compas.geometry import Point
    from compas.geometry import Surface


def _dispatch(name: str, *args: Any, **kwargs: Any) -> Any:
    from compas_occ import intersections

    return getattr(intersections, name)(*args, **kwargs)


@plugin(category="intersections", requires=["OCC"])
def intersection_line_surface(line: "Line", surface: "Surface", tol: float | None = None) -> "IntersectionResult[Point]":
    return _dispatch("intersection_line_surface", line, surface, tol=tol)


@plugin(category="intersections", requires=["OCC"])
def intersection_plane_surface(plane: "Plane", surface: "Surface", tol: float | None = None) -> "IntersectionResult[Curve | Line]":
    return _dispatch("intersection_plane_surface", plane, surface, tol=tol)


@plugin(category="intersections", requires=["OCC"])
def intersection_curve_surface(curve: "Curve", surface: "Surface", tol: float | None = None) -> "IntersectionResult[Point]":
    return _dispatch("intersection_curve_surface", curve, surface, tol=tol)


@plugin(category="intersections", requires=["OCC"])
def intersection_surface_surface(surface_a: "Surface", surface_b: "Surface", tol: float | None = None) -> "IntersectionResult[Curve | Line]":
    return _dispatch("intersection_surface_surface", surface_a, surface_b, tol=tol)


@plugin(category="intersections", requires=["OCC"])
def intersection_line_brep(line: "Line", brep: "Brep", tol: float | None = None) -> "IntersectionResult[Point]":
    return _dispatch("intersection_line_brep", line, brep, tol=tol)


@plugin(category="intersections", requires=["OCC"])
def intersection_plane_brep(plane: "Plane", brep: "Brep", tol: float | None = None) -> "IntersectionResult[Curve | Line]":
    return _dispatch("intersection_plane_brep", plane, brep, tol=tol)


@plugin(category="intersections", requires=["OCC"])
def intersection_curve_brep(curve: "Curve", brep: "Brep", tol: float | None = None) -> "IntersectionResult[Point]":
    return _dispatch("intersection_curve_brep", curve, brep, tol=tol)


@plugin(category="intersections", requires=["OCC"])
def intersection_surface_brep(surface: "Surface", brep: "Brep", tol: float | None = None) -> "IntersectionResult[Curve | Line]":
    return _dispatch("intersection_surface_brep", surface, brep, tol=tol)
