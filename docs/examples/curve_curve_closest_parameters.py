from compas.geometry import Point, Polyline
from compas_occ.geometry import OCCNurbsCurve as NurbsCurve

from compas_view2.app import App

points0 = [Point(0, 0, 0), Point(3, 6, 0), Point(6, -3, 3), Point(10, 0, 0)]
curve0 = NurbsCurve.from_points(points0)

points1 = [Point(6, -3, 0), Point(3, 1, 0), Point(6, 6, 3), Point(3, 12, 0)]
curve1 = NurbsCurve.from_points(points1)

parameters, distance = curve0.curve_closest_parameters(curve1, return_distance=True)

print(parameters)
print(distance)

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

view.add(Polyline(curve0.locus()), linewidth=3)
view.add(Polyline(curve1.locus()), linewidth=3)

view.add(curve0.point_at(parameters[0]), pointcolor=(1, 0, 0))
view.add(curve1.point_at(parameters[1]), pointcolor=(1, 0, 0))

view.run()
