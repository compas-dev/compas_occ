from compas.geometry import Point, Polyline, Bezier
from compas_occ.geometry import NurbsCurve

from compas_view2.app import App
from compas_view2.objects import Collection

points = [Point(0, 0, 0), Point(3, 6, 0), Point(6, -3, 3), Point(10, 0, 0)]
bezier = Bezier(points)
points = bezier.locus(10)

curve = NurbsCurve.from_interpolation(points)

print(curve)

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

view.add(Polyline(curve.locus()), linewidth=3)
view.add(Collection(points))

# view.add(Polyline(curve.points), show_points=True, pointsize=20, pointcolor=(1, 0, 0), linewidth=1, linecolor=(0.3, 0.3, 0.3))

view.run()
