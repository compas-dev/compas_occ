from compas.geometry import Point, Polyline
from compas_occ.geometry import OCCNurbsCurve as NurbsCurve

from compas_view2.app import App

points = [Point(0, 0, 0), Point(3, 0, 2), Point(6, 0, -3), Point(8, 0, 0)]
curve = NurbsCurve.from_interpolation(points)

projection_point = Point(2, -1, 0)

closest_point, t = curve.closest_point(projection_point, parameter=True)

print(curve.point_at(t) == closest_point)

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

view.add(Polyline(curve.locus()), linewidth=3)
view.add(projection_point, pointcolor=(0, 0, 1))
view.add(closest_point, pointcolor=(1, 0, 0))

view.run()
