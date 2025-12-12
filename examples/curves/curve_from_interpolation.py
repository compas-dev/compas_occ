from compas_viewer import Viewer

from compas.geometry import Bezier
from compas.geometry import NurbsCurve
from compas.geometry import Point

points = [Point(0, 0, 0), Point(3, 6, 0), Point(6, -3, 3), Point(10, 0, 0)]
bezier = Bezier(points)
points = bezier.to_points(10)

curve = NurbsCurve.from_interpolation(points)

# ==============================================================================
# Visualisation
# ==============================================================================

viewer = Viewer()

viewer.scene.add(curve, linewidth=2)
viewer.scene.add(points, pointsize=20)

viewer.show()
