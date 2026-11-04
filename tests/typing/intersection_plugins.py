from typing import assert_type
from typing import cast

from compas.geometry import Brep
from compas.geometry import Curve
from compas.geometry import IntersectionResult
from compas.geometry import Line
from compas.geometry import Plane
from compas.geometry import Point
from compas.geometry import Surface
from compas_occ.plugins.intersections import intersection_curve_brep
from compas_occ.plugins.intersections import intersection_curve_surface
from compas_occ.plugins.intersections import intersection_line_brep
from compas_occ.plugins.intersections import intersection_line_surface
from compas_occ.plugins.intersections import intersection_plane_brep
from compas_occ.plugins.intersections import intersection_plane_surface
from compas_occ.plugins.intersections import intersection_surface_brep
from compas_occ.plugins.intersections import intersection_surface_surface

line = Line([0, 0, 0], [1, 0, 0])
plane = Plane.worldXY()
curve = cast(Curve, object())
surface = cast(Surface, object())
brep = cast(Brep, object())

assert_type(intersection_line_surface(line, surface), IntersectionResult[Point])
assert_type(intersection_plane_surface(plane, surface), IntersectionResult[Curve | Line])
assert_type(intersection_curve_surface(curve, surface), IntersectionResult[Point])
assert_type(intersection_surface_surface(surface, surface), IntersectionResult[Curve | Line])
assert_type(intersection_line_brep(line, brep), IntersectionResult[Point])
assert_type(intersection_plane_brep(plane, brep), IntersectionResult[Curve | Line])
assert_type(intersection_curve_brep(curve, brep), IntersectionResult[Point])
assert_type(intersection_surface_brep(surface, brep, tol=1e-6), IntersectionResult[Curve | Line])
