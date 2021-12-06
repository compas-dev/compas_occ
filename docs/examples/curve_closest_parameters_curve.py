from compas.geometry import Point, Polyline
from compas.geometry import NurbsCurve

from compas_view2.app import App

points0 = [Point(0, 0, 0), Point(3, 6, 0), Point(6, -3, 3), Point(10, 0, 0)]
curve0 = NurbsCurve.from_points(points0)

points1 = [Point(6, -3, 0), Point(3, 1, 0), Point(6, 6, 3), Point(3, 12, 0)]
curve1 = NurbsCurve.from_points(points1)

parameters, distance = curve0.closest_parameters_curve(curve1, return_distance=True)

print(parameters)
print(distance)

points = curve0.closest_points_curve(curve1, return_distance=False)

print(points)

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

view.add(Polyline(curve0.locus()), linewidth=3)
view.add(Polyline(curve1.locus()), linewidth=3)

view.add(points[0], pointcolor=(1, 0, 0))
view.add(points[1], pointcolor=(1, 0, 0))

view.run()
