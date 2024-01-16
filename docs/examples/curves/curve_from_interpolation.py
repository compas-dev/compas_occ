# type: ignore

from compas.geometry import Point
from compas.geometry import Bezier
from compas.geometry import NurbsCurve
from compas_view2.app import App
from compas_view2.objects import Collection


points = [Point(0, 0, 0), Point(3, 6, 0), Point(6, -3, 3), Point(10, 0, 0)]
bezier = Bezier(points)
points = bezier.to_points(10)

curve = NurbsCurve.from_interpolation(points)

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

view.add(curve.to_polyline(), linewidth=3)
view.add(Collection(points))

view.run()
