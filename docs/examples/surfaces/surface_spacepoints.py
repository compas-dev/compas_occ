from compas.geometry import NurbsSurface
from compas.geometry import Point
from compas.geometry import Polyline
from compas.itertools import flatten
from compas.itertools import linspace
from compas.itertools import meshgrid
from compas_viewer import Viewer

points = [
    [Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0), Point(3, 0, 0), Point(4, 0, 0)],
    [Point(0, 1, 0), Point(1, 1, 2), Point(2, 1, 2), Point(3, 1, 0), Point(4, 1, 0)],
    [Point(0, 2, 0), Point(1, 2, 2), Point(2, 2, 2), Point(3, 2, 0), Point(4, 2, 0)],
    [Point(0, 3, 0), Point(1, 3, 0), Point(2, 3, 0), Point(3, 3, 0), Point(4, 3, 0)],
]

surface = NurbsSurface.from_points(points=points)

# ==============================================================================
# Points over UV space
# ==============================================================================

U, V = meshgrid(linspace(*surface.domain_u), linspace(*surface.domain_v), "ij")
spacepoints = [surface.point_at(u, v) for u, v in zip(flatten(U), flatten(V))]

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
        lineswidth=2,
        linecolor=(1.0, 0.5, 0.5),
    )

for col in zip(*surface.points):
    viewer.scene.add(
        Polyline(col),
        show_points=True,
        pointsize=20,
        pointcolor=(1, 0, 0),
        lineswidth=2,
        linecolor=(0.5, 1.0, 0.5),
    )

viewer.scene.add(surface)
# viewer.scene.add(Collection(spacepoints))
viewer.show()
