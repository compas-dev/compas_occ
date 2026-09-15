# type: ignore
from compas_viewer import Viewer

from compas.geometry import NurbsSurface
from compas.geometry import Point
from compas.geometry import Sphere
from compas_occ.brep import OCCBrep

points = [
    [Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0), Point(3, 0, 0)],
    [Point(0, 1, 0), Point(1, 1, 2), Point(2, 1, 2), Point(3, 1, 0)],
    [Point(0, 2, 0), Point(1, 2, 2), Point(2, 2, 2), Point(3, 2, 0)],
    [Point(0, 3, 0), Point(1, 3, 0), Point(2, 3, 0), Point(3, 3, 0)],
]

surface = OCCBrep.from_surface(NurbsSurface.from_points(points=points))
sphere = OCCBrep.from_sphere(Sphere(radius=1))

x = surface.intersect(sphere)
assert x, "..."

curves = []
for edge in x.edges:
    curves.append(edge.curve)

# =============================================================================
# Visualization
# =============================================================================

viewer = Viewer()
viewer.scene.add(surface, linewidth=2, show_points=False, opacity=0.5)
viewer.scene.add(sphere, linewidth=2, show_points=False, opacity=0.5)
viewer.scene.add(curves, linewidth=2)
viewer.show()
