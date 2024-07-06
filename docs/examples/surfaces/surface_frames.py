from compas.geometry import NurbsSurface
from compas.geometry import Point
from compas.itertools import flatten
from compas.itertools import linspace
from compas.itertools import meshgrid
from compas_viewer import Viewer
from compas_viewer.scene import Collection

points = [
    [Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0), Point(3, 0, 0)],
    [Point(0, 1, 0), Point(1, 1, 2), Point(2, 1, 2), Point(3, 1, 0)],
    [Point(0, 2, 0), Point(1, 2, 2), Point(2, 2, 2), Point(3, 2, 0)],
    [Point(0, 3, 0), Point(1, 3, 0), Point(2, 3, 0), Point(3, 3, 0)],
]

surface = NurbsSurface.from_points(points=points)

# ==============================================================================
# Frames
# ==============================================================================

U, V = meshgrid(linspace(*surface.domain_u), linspace(*surface.domain_v), "ij")
frames = [surface.frame_at(u, v) for u, v in zip(flatten(U), flatten(V))]

# ==============================================================================
# Visualisation
# ==============================================================================

viewer = Viewer()

viewer.scene.add(surface, show_lines=False)
viewer.scene.add(Collection(frames), size=0.1, pointsize=0.25)  # type: ignore

viewer.show()
