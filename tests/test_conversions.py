import pytest
import numpy as np

from compas.geometry import Pointcloud
from compas.tolerance import TOL
from compas_occ.conversions import array1_from_points1
from compas_occ.conversions import compas_transformation_to_trsf
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


def test_transformation_normalizes_numpy_scalars_at_occ_boundary():
    trsf = compas_transformation_to_trsf(
        [
            [np.float64(1.0), np.float64(0.0), np.float64(0.0), np.float64(2.0)],
            [np.float64(0.0), np.float64(1.0), np.float64(0.0), np.float64(3.0)],
            [np.float64(0.0), np.float64(0.0), np.float64(1.0), np.float64(4.0)],
            [np.float64(0.0), np.float64(0.0), np.float64(0.0), np.float64(1.0)],
        ]
    )

    assert trsf.Value(1, 4) == pytest.approx(2.0)
    assert trsf.Value(2, 4) == pytest.approx(3.0)
    assert trsf.Value(3, 4) == pytest.approx(4.0)


@pytest.mark.parametrize(
    ("matrix", "message"),
    [
        (
            [
                [1.0, 2.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            "shear or nonuniform",
        ),
        (
            [
                [2.0, 0.0, 0.0, 0.0],
                [0.0, 3.0, 0.0, 0.0],
                [0.0, 0.0, 4.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            "shear or nonuniform",
        ),
        (
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.25, 1.0],
            ],
            "projective",
        ),
    ],
)
def test_transformation_rejects_unsupported_occ_matrices(matrix, message):
    with pytest.raises(ValueError, match=message):
        compas_transformation_to_trsf(matrix)
