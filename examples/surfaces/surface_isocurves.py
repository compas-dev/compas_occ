from compas_viewer import Viewer

from compas.colors import Color
from compas.geometry import NurbsSurface
from compas.geometry import Point

points = [
    [Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0), Point(3, 0, 0), Point(4, 0, 0)],
    [Point(0, 1, 0), Point(1, 1, 2), Point(2, 1, 2), Point(3, 1, 0), Point(4, 1, 0)],
    [Point(0, 2, 0), Point(1, 2, 2), Point(2, 2, 2), Point(3, 2, 0), Point(4, 2, 0)],
    [Point(0, 3, 0), Point(1, 3, 0), Point(2, 3, 0), Point(3, 3, 0), Point(4, 3, 0)],
]

surface = NurbsSurface.from_points(points=points)

# ==============================================================================
# Visualisation
# ==============================================================================

viewer = Viewer()

u_curves = []
for u in surface.space_u(17):  # type: ignore
    u_curves.append(surface.isocurve_u(u).to_polyline())

v_curves = []
for v in surface.space_v(17):  # type: ignore
    v_curves.append(surface.isocurve_v(v).to_polyline())

viewer.scene.add(u_curves, linecolor=Color.red(), linewidth=3)
viewer.scene.add(v_curves, linecolor=Color.green(), linewidth=3)

viewer.show()
