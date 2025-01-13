import pytest

from compas.geometry import Pointcloud
from compas.tolerance import TOL
from compas_occ.conversions import array1_from_points1
from compas_occ.conversions import harray1_from_points1
from compas_occ.conversions import points1_from_array1


@pytest.mark.parametrize(
    "points1",
    [
        Pointcloud.from_bounds(10, 10, 10, 1),
        Pointcloud.from_bounds(10, 10, 10, 17),
        Pointcloud.from_bounds(10, 10, 10, 53),
    ],
)
def test_array1_from_points1(points1):
    array1 = array1_from_points1(points1)
    assert array1.Length() == len(points1)

    for item, point in zip(array1, points1):
        assert TOL.is_close(point.x, item.X())
        assert TOL.is_close(point.y, item.Y())
        assert TOL.is_close(point.z, item.Z())


@pytest.mark.parametrize(
    "points1",
    [
        Pointcloud.from_bounds(10, 10, 10, 1),
        Pointcloud.from_bounds(10, 10, 10, 17),
        Pointcloud.from_bounds(10, 10, 10, 53),
    ],
)
def test_harray1_from_points1(points1):
    array1 = harray1_from_points1(points1)
    assert array1.Length() == len(points1)

    for item, point in zip(array1, points1):
        assert TOL.is_close(point.x, item.X())
        assert TOL.is_close(point.y, item.Y())
        assert TOL.is_close(point.z, item.Z())


@pytest.mark.parametrize(
    "points1",
    [
        Pointcloud.from_bounds(10, 10, 10, 1),
        Pointcloud.from_bounds(10, 10, 10, 17),
        Pointcloud.from_bounds(10, 10, 10, 53),
    ],
)
def test_points1_from_array1(points1):
    array1 = array1_from_points1(points1)
    points1 = points1_from_array1(array1)
    assert array1.Length() == len(points1)

    for item, point in zip(array1, points1):
        assert TOL.is_close(point.x, item.X())
        assert TOL.is_close(point.y, item.Y())
        assert TOL.is_close(point.z, item.Z())
