from typing import assert_type

from compas.geometry import NurbsSurface
from compas.geometry import Plane
from compas.geometry import Surface
from compas_occ.plugins.surfaces import from_interpolation
from compas_occ.plugins.surfaces import from_native
from compas_occ.plugins.surfaces import from_parameters
from compas_occ.plugins.surfaces import from_plane
from compas_occ.plugins.surfaces import from_points
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
