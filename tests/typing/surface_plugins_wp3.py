from collections.abc import Sequence
from typing import assert_type
from typing import cast

from compas.geometry import Brep
from compas.geometry import Curve
from compas.geometry import Frame
from compas.geometry import Line
from compas.geometry import NurbsCurve
from compas.geometry import NurbsSurface
from compas.geometry import Plane
from compas.geometry import Point
from compas.geometry import Surface
from compas.geometry import Transformation
from compas.geometry import Vector
from compas_occ.plugins.surfaces import from_extrusion
from compas_occ.plugins.surfaces import from_fill
from compas_occ.plugins.surfaces import from_frame
from compas_occ.plugins.surfaces import from_interpolation
from compas_occ.plugins.surfaces import from_native
from compas_occ.plugins.surfaces import from_parameters
from compas_occ.plugins.surfaces import from_plane
from compas_occ.plugins.surfaces import from_points
from compas_occ.plugins.surfaces import from_step
from compas_occ.plugins.surfaces import surface_boundary
from compas_occ.plugins.surfaces import surface_closest_point
from compas_occ.plugins.surfaces import surface_degree_u
from compas_occ.plugins.surfaces import surface_degree_v
from compas_occ.plugins.surfaces import surface_domain_u
from compas_occ.plugins.surfaces import surface_domain_v
from compas_occ.plugins.surfaces import surface_frame_at
from compas_occ.plugins.surfaces import surface_is_periodic_u
from compas_occ.plugins.surfaces import surface_is_periodic_v
from compas_occ.plugins.surfaces import surface_isocurve_u
from compas_occ.plugins.surfaces import surface_isocurve_v
from compas_occ.plugins.surfaces import surface_knots_u
from compas_occ.plugins.surfaces import surface_knots_v
from compas_occ.plugins.surfaces import surface_mults_u
from compas_occ.plugins.surfaces import surface_mults_v
from compas_occ.plugins.surfaces import surface_normal_at
from compas_occ.plugins.surfaces import surface_point_at
from compas_occ.plugins.surfaces import surface_points
from compas_occ.plugins.surfaces import surface_to_brep
from compas_occ.plugins.surfaces import surface_to_step
from compas_occ.plugins.surfaces import surface_transform
from compas_occ.plugins.surfaces import surface_weights
from compas_occ.plugins.surfaces import surface_from_native


class CustomSurface(Surface):
    pass


points = [
    [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
    [[1.0, 0.0, 0.0], [1.0, 1.0, 0.0]],
]
weights = [[1.0, 1.0], [1.0, 1.0]]

assert_type(surface_from_native(CustomSurface, object()), CustomSurface)
assert_type(from_interpolation(points, precision=1e-3), NurbsSurface)
assert_type(from_native(object()), NurbsSurface)
assert_type(
    from_parameters(
        points,
        weights,
        knots_u=[0.0, 1.0],
        knots_v=[0.0, 1.0],
        mults_u=[2, 2],
        mults_v=[2, 2],
        degree_u=1,
        degree_v=1,
        is_periodic_u=False,
        is_periodic_v=False,
    ),
    NurbsSurface,
)
assert_type(from_plane(Plane.worldXY()), NurbsSurface)
assert_type(from_points(points, degree_u=1, degree_v=1), NurbsSurface)

curve = cast(NurbsCurve, object())
surface = cast(NurbsSurface, object())
assert_type(from_extrusion(curve, Vector(0.0, 0.0, 1.0)), NurbsSurface)
assert_type(from_fill(curve, curve), NurbsSurface)
assert_type(from_frame(Frame.worldXY()), NurbsSurface)
assert_type(from_step("surface.step"), NurbsSurface)
assert_type(surface_points(surface), Sequence[Sequence[Point]])
assert_type(surface_weights(surface), Sequence[Sequence[float]])
assert_type(surface_knots_u(surface), Sequence[float])
assert_type(surface_knots_v(surface), Sequence[float])
assert_type(surface_mults_u(surface), Sequence[int])
assert_type(surface_mults_v(surface), Sequence[int])
assert_type(surface_degree_u(surface), int)
assert_type(surface_degree_v(surface), int)
assert_type(surface_domain_u(surface), tuple[float, float])
assert_type(surface_domain_v(surface), tuple[float, float])
assert_type(surface_is_periodic_u(surface), bool)
assert_type(surface_is_periodic_v(surface), bool)
assert_type(surface_isocurve_u(surface, 0.5), Curve | Line)
assert_type(surface_isocurve_v(surface, 0.5), Curve | Line)
assert_type(surface_boundary(surface), list[Curve | Line])
assert_type(surface_point_at(surface, 0.5, 0.5), Point)
assert_type(surface_normal_at(surface, 0.5, 0.5), Vector)
assert_type(surface_frame_at(surface, 0.5, 0.5), Frame)
assert_type(surface_closest_point(surface, points[0][0]), Point | tuple[Point, tuple[float, float]] | None)
assert_type(surface_transform(surface, Transformation()), None)
assert_type(surface_to_brep(surface), Brep)
assert_type(surface_to_step(surface, "surface.step"), None)
