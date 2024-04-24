from compas.geometry import NurbsSurface
from compas.geometry import Point
from compas.geometry import Polyline
from compas_viewer import Viewer

points = [
    [
        Point(0, 0, 0),
        Point(1, 0, +0),
        Point(2, 0, +0),
        Point(3, 0, +0),
        Point(4, 0, +0),
        Point(5, 0, 0),
    ],
    [
        Point(0, 1, 0),
        Point(1, 1, -1),
        Point(2, 1, -1),
        Point(3, 1, -1),
        Point(4, 1, -1),
        Point(5, 1, 0),
    ],
    [
        Point(0, 2, 0),
        Point(1, 2, -1),
        Point(2, 2, +2),
        Point(3, 2, +2),
        Point(4, 2, -1),
        Point(5, 2, 0),
    ],
    [
        Point(0, 3, 0),
        Point(1, 3, -1),
        Point(2, 3, +2),
        Point(3, 3, +2),
        Point(4, 3, -1),
        Point(5, 3, 0),
    ],
    [
        Point(0, 4, 0),
        Point(1, 4, -1),
        Point(2, 4, -1),
        Point(3, 4, -1),
        Point(4, 4, -1),
        Point(5, 4, 0),
    ],
    [
        Point(0, 5, 0),
        Point(1, 5, +0),
        Point(2, 5, +0),
        Point(3, 5, +0),
        Point(4, 5, +0),
        Point(5, 5, 0),
    ],
]

weights = [
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
]

surface = NurbsSurface.from_parameters(
    points=points,
    weights=weights,
    knots_u=[
        1.0,
        1 + 1 / 9,
        1 + 2 / 9,
        1 + 3 / 9,
        1 + 4 / 9,
        1 + 5 / 9,
        1 + 6 / 9,
        1 + 7 / 9,
        1 + 8 / 9,
        2.0,
    ],
    knots_v=[0.0, 1 / 9, 2 / 9, 3 / 9, 4 / 9, 5 / 9, 6 / 9, 7 / 9, 8 / 9, 1.0],
    mults_u=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    mults_v=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    degree_u=3,
    degree_v=3,
)

# ==============================================================================
# Visualisation
# ==============================================================================

viewer = Viewer()

for row in surface.points:
    viewer.scene.add(
        Polyline(row),
        show_points=True,
        pointsize=20,
        pointcolor=(1, 0, 0),
        linewidth=2,
        linecolor=(0.3, 0.3, 0.3),
    )

for col in zip(*surface.points):
    viewer.scene.add(
        Polyline(col),
        show_points=True,
        pointsize=20,
        pointcolor=(1, 0, 0),
        linewidth=2,
        linecolor=(0.3, 0.3, 0.3),
    )

viewer.scene.add(surface.to_mesh())
viewer.show()
