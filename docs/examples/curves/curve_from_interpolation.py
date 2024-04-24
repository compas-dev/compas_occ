from compas.geometry import Bezier
from compas.geometry import NurbsCurve
from compas.geometry import Point
from compas_viewer import Viewer

points = [Point(0, 0, 0), Point(3, 6, 0), Point(6, -3, 3), Point(10, 0, 0)]
bezier = Bezier(points)
points = bezier.to_points(10)

curve = NurbsCurve.from_interpolation(points)

# ==============================================================================
# Visualisation
# ==============================================================================

viewer = Viewer()

viewer.scene.add(curve.to_polyline(), linewidth=3)
# viewer.scene.add(Collection(points))

viewer.show()
