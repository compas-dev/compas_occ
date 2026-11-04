from typing import assert_type

from compas.geometry import Box
from compas.geometry import Point
from compas.geometry import Surface
from compas_occ.geometry import OCCNurbsSurface


def consume_surface(surface: Surface) -> None:
    assert_type(surface.aabb, Box)
    assert_type(surface.obb, Box)
    assert_type(surface.closest_point([0.0, 0.0, 0.0]), Point | None)
    assert_type(
        surface.closest_point([0.0, 0.0, 0.0], return_parameters=True),
        tuple[Point, tuple[float, float]] | None,
    )
    assert_type(surface.copy(copy_guid=True), Surface)


surface = OCCNurbsSurface.from_points(
    [
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
        [[0.0, 1.0, 0.0], [1.0, 1.0, 0.0]],
    ],
    degree_u=1,
    degree_v=1,
)
consume_surface(surface)
assert_type(surface.points[0], list[Point])
assert_type(surface.points[0, 0], Point)
