from compas.colors import Color
from compas.geometry import NurbsCurve
from compas.geometry import Point
from compas_viewer import Viewer

points = [Point(0, 0, 0), Point(3, 0, 2), Point(6, 0, -3), Point(8, 0, 0)]
curve = NurbsCurve.from_interpolation(points)

point = Point(2, -1, 0)
closest, t = curve.closest_point(point, return_parameter=True)  # type: ignore

# =============================================================================
# Visualization
# =============================================================================

viewer = Viewer()

viewer.scene.add(curve, linewidth=3)
viewer.scene.add(point, pointcolor=Color(0, 0, 1), pointsize=20, name="Point")
viewer.scene.add(closest, pointcolor=Color(1, 0, 0), pointsize=20, name="Closest")

viewer.show()
