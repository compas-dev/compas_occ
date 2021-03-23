import pytest
from OCC.Core.gp import gp_Ax3
from compas.geometry import Frame, Vector, Point, Box

X_AXE = [10, 0, 0]
Y_AXE = [0, 10, 0]
ORIGIN = [10, 10, 10]


@pytest.fixture
def frame(point, x_vector, y_vector) -> Frame:
    return Frame(point, x_vector, y_vector)


@pytest.fixture
def point() -> Point:
    return Point(*ORIGIN)


@pytest.fixture
def x_vector() -> Vector:
    return Vector(*X_AXE)


@pytest.fixture
def y_vector() -> Vector:
    return Vector(*Y_AXE)


@pytest.fixture
def gp_ax3() -> gp_Ax3:
    return gp_Ax3()

@pytest.fixture
def box(frame) -> Box:
    return Box(frame, 10, 10, 10)

