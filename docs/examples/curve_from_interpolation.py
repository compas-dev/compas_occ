from compas.geometry import Point
from compas.geometry import Polyline, Bezier
from compas_occ.geometry import NurbsCurve
from compas_view2.app import App
from compas_view2.objects import Collection


points = [Point(0, 0, 0), Point(3, 6, 0), Point(6, -3, 3), Point(10, 0, 0)]
bezier = Bezier(points)
points = bezier.locus(10)

curve = NurbsCurve.from_interpolation(points)

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

view.add(Polyline(curve.locus()), linewidth=3)
view.add(Collection(points))

view.run()
