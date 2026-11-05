from typing import assert_type
from typing import cast

from compas.geometry import NurbsCurve
from compas.geometry import Point
from compas.geometry import Transformation
from compas.geometry import Vector
from compas_occ.geometry import OCCCurve
from compas_occ.plugins.curves import curve_closest_point
from compas_occ.plugins.curves import curve_continuity
from compas_occ.plugins.curves import curve_curvature_at
from compas_occ.plugins.curves import curve_degree
from compas_occ.plugins.curves import curve_divide_by_count
from compas_occ.plugins.curves import curve_divide_by_length
from compas_occ.plugins.curves import curve_domain
from compas_occ.plugins.curves import curve_from_native
from compas_occ.plugins.curves import curve_is_closed
from compas_occ.plugins.curves import curve_is_periodic
from compas_occ.plugins.curves import curve_is_rational
from compas_occ.plugins.curves import curve_knots
from compas_occ.plugins.curves import curve_length
from compas_occ.plugins.curves import curve_multiplicities
from compas_occ.plugins.curves import curve_normal_at
from compas_occ.plugins.curves import curve_point_at
from compas_occ.plugins.curves import curve_points
from compas_occ.plugins.curves import curve_reverse
from compas_occ.plugins.curves import curve_tangent_at
from compas_occ.plugins.curves import curve_to_step
from compas_occ.plugins.curves import curve_transform
from compas_occ.plugins.curves import curve_weights
from compas_occ.plugins.curves import from_interpolation
from compas_occ.plugins.curves import from_native
from compas_occ.plugins.curves import from_parameters
from compas_occ.plugins.curves import from_points
from compas_occ.plugins.curves import from_step


points = [(0.0, 0.0, 0.0), (1.0, 1.0, 0.0), (2.0, 0.0, 0.0)]

assert_type(curve_from_native(OCCCurve, object()), OCCCurve)
assert_type(from_native(object()), NurbsCurve)
assert_type(from_interpolation(points, precision=1e-4), NurbsCurve)
assert_type(from_parameters(points, [1.0, 1.0, 1.0], [0.0, 1.0], [3, 3], 2), NurbsCurve)
assert_type(from_points(points, degree=2, is_periodic=False), NurbsCurve)

curve = cast(NurbsCurve, object())
assert_type(from_step("curve.step"), NurbsCurve)
assert_type(curve_points(curve), list[Point])
assert_type(curve_weights(curve), list[float])
assert_type(curve_knots(curve), list[float])
assert_type(curve_multiplicities(curve), list[int])
assert_type(curve_continuity(curve), int)
assert_type(curve_degree(curve), int)
assert_type(curve_is_rational(curve), bool)
assert_type(curve_domain(curve), tuple[float, float])
assert_type(curve_length(curve), float)
assert_type(curve_is_closed(curve), bool)
assert_type(curve_is_periodic(curve), bool)
assert_type(curve_point_at(curve, 0.5), Point)
assert_type(curve_normal_at(curve, 0.5), Vector | None)
assert_type(curve_tangent_at(curve, 0.5), Vector)
assert_type(curve_curvature_at(curve, 0.5), Vector)
assert_type(curve_transform(curve, Transformation()), None)
assert_type(curve_reverse(curve), None)
assert_type(curve_closest_point(curve, points[0]), Point | tuple[Point, float])
assert_type(curve_divide_by_count(curve, 4), list[float] | tuple[list[float], list[Point]])
assert_type(curve_divide_by_length(curve, 0.5), list[float] | tuple[list[float], list[Point]])
assert_type(curve_to_step(curve, "curve.step"), None)
