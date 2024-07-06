from compas.colors import Color
from compas.geometry import NurbsCurve
from compas.geometry import Point
from compas_viewer import Viewer

curve0: NurbsCurve
curve1: NurbsCurve

points0 = [Point(0, 0, 0), Point(3, 6, 0), Point(6, -3, 3), Point(10, 0, 0)]
curve0 = NurbsCurve.from_points(points0)

points1 = [Point(6, -3, 0), Point(3, 1, 0), Point(6, 6, 3), Point(3, 12, 0)]
curve1 = NurbsCurve.from_points(points1)

parameters, distance = curve0.closest_parameters_curve(curve1, return_distance=True)  # type: ignore
points = curve0.closest_points_curve(curve1, return_distance=False)

# =============================================================================
# Visualization
# =============================================================================

viewer = Viewer()

viewer.scene.add(curve0, linewidth=3)
viewer.scene.add(curve1, linewidth=3)

viewer.scene.add(list(points), pointcolor=Color(1, 0, 0), pointsize=20)

viewer.show()
