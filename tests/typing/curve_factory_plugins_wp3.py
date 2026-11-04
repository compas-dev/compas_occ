from typing import assert_type

from compas.geometry import NurbsCurve
from compas_occ.geometry import OCCCurve
from compas_occ.plugins.curves import curve_from_native
from compas_occ.plugins.curves import from_interpolation
from compas_occ.plugins.curves import from_native
from compas_occ.plugins.curves import from_parameters
from compas_occ.plugins.curves import from_points


points = [(0.0, 0.0, 0.0), (1.0, 1.0, 0.0), (2.0, 0.0, 0.0)]

assert_type(curve_from_native(OCCCurve, object()), OCCCurve)
assert_type(from_native(object()), NurbsCurve)
assert_type(from_interpolation(points, precision=1e-4), NurbsCurve)
assert_type(from_parameters(points, [1.0, 1.0, 1.0], [0.0, 1.0], [3, 3], 2), NurbsCurve)
assert_type(from_points(points, degree=2, is_periodic=False), NurbsCurve)
