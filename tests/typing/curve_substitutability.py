from typing import assert_type
from typing import cast

from compas.geometry import Box
from compas.geometry import Curve
from compas.geometry import Point
from compas.geometry import Polyline
from compas.geometry import Vector
from compas_occ.geometry import OCCCurve
from compas_occ.geometry import OCCCurve2d
from compas_occ.geometry import OCCNurbsCurve


curve = cast(OCCCurve, object())
base_curve: Curve = curve

assert_type(base_curve.point_at(0.5, world=True), Point)
assert_type(base_curve.tangent_at(0.5, world=True), Vector)
assert_type(base_curve.to_polyline(n=8, domain=(0.0, 1.0)), Polyline)
assert_type(base_curve.length, float)
assert_type(base_curve.aabb, Box)
assert_type(curve.closest_point([0.0, 0.0, 0.0]), Point)
assert_type(curve.closest_point([0.0, 0.0, 0.0], return_parameter=True), tuple[Point, float])
assert_type(curve.divide_by_count(4), list[float])
assert_type(curve.divide_by_count(4, return_points=True), tuple[list[float], list[Point]])
assert_type(curve.copy(), OCCCurve)
assert_type(cast(OCCCurve2d, object()).copy(copy_guid=True), OCCCurve2d)
assert_type(cast(OCCNurbsCurve, object()).copy(), OCCNurbsCurve)
