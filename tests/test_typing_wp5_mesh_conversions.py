import pytest

from compas.geometry import Point
from compas_occ.conversions import quad_to_face


@pytest.mark.parametrize(
    "quad",
    [
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]],
        [Point(0.0, 0.0, 0.0), Point(1.0, 0.0, 0.0), Point(1.0, 1.0, 0.0), Point(0.0, 1.0, 0.0)],
    ],
)
def test_quad_to_face_accepts_coordinate_sequences(quad):
    face = quad_to_face(quad)

    assert not face.IsNull()
