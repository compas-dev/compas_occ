# type: ignore

from compas.geometry import Point
from compas.geometry import NurbsCurve
from compas_view2.app import App

points1 = [Point(0, 0, 0), Point(1, 1, 0), Point(3, 0, 0)]
points2 = [Point(3, 0, 0), Point(4, -2, 0), Point(5, 0, 0)]

curve1 = NurbsCurve.from_interpolation(points1)
curve2 = NurbsCurve.from_interpolation(points2)

joined = curve1.joined(curve2)
curve1.join(curve2)

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

view.add(curve1.to_polyline(), linewidth=3, linecolor=(1, 0, 0))
view.add(curve2.to_polyline(), linewidth=3, linecolor=(0, 1, 0))
view.add(joined.to_polyline(), linewidth=3, linecolor=(0, 0, 1))

view.run()
