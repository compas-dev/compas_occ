from compas.colors import Color
from compas.geometry import NurbsCurve
from compas.geometry import Point
from compas_viewer import Viewer

points1 = [Point(0, 0, 0), Point(1, 1, 0), Point(3, 0, 0)]
points2 = [Point(3, 0, 0), Point(4, -2, 0), Point(5, 0, 0)]

curve1 = NurbsCurve.from_interpolation(points1)
curve2 = NurbsCurve.from_interpolation(points2)

joined = curve1.joined(curve2)

# ==============================================================================
# Visualisation
# ==============================================================================

viewer = Viewer()

viewer.scene.add(curve1.to_polyline(), lineswidth=3, linecolor=Color.red(), show_points=False)
viewer.scene.add(curve2.to_polyline(), lineswidth=3, linecolor=Color.green(), show_points=False)
viewer.scene.add(joined.to_polyline(), lineswidth=3, linecolor=Color.blue(), show_points=False)

viewer.show()
