from math import radians

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

for row in surface.points:
    viewer.scene.add(
        Polyline(row),
        show_points=True,
        pointsize=20,
        pointcolor=(1, 0, 0),
        linewidth=2,
        linecolor=(1.0, 0, 0),
    )

for col in zip(*surface.points):
    viewer.scene.add(Polyline(col), linewidth=2, linecolor=(0, 1.0, 0))

viewer.scene.add(surface, show_lines=False)
viewer.scene.add(box, show_faces=False)

viewer.show()
