from math import radians

from compas.colors import Color
from compas.geometry import NurbsSurface
from compas.geometry import Point
from compas.geometry import Polyline
from compas.geometry import Rotation
from compas.geometry import Translation
from compas_viewer import Viewer

points = [
    [Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0), Point(3, 0, 0), Point(4, 0, 0)],
    [Point(0, 1, 0), Point(1, 1, 2), Point(2, 1, 2), Point(3, 1, 0), Point(4, 1, 0)],
    [Point(0, 2, 0), Point(1, 2, 2), Point(2, 2, 2), Point(3, 2, 0), Point(4, 2, 0)],
    [Point(0, 3, 0), Point(1, 3, 0), Point(2, 3, 0), Point(3, 3, 0), Point(4, 3, 0)],
]

surface = NurbsSurface.from_points(points=points)

T = Translation.from_vector([0, -1.5, 0])
R = Rotation.from_axis_and_angle([0, 0, 1], radians(45))

surface.transform(R * T)

# ==============================================================================
# AABB
# ==============================================================================

box = surface.aabb()

# ==============================================================================
# Visualisation
# ==============================================================================

viewer = Viewer()

points = list(surface.points)
u_direction = [Polyline(row) for row in points]
v_direction = [Polyline(col) for col in zip(*points)]

viewer.scene.add(
    u_direction,
    linewidth=2,
    linecolor=Color.red(),
)
viewer.scene.add(
    v_direction,
    linewidth=2,
    linecolor=Color.green(),
)
viewer.scene.add(points, pointsize=20)


viewer.scene.add(surface, show_lines=False)
viewer.scene.add(box, show_faces=False)

viewer.show()
