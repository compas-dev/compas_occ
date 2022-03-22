from compas.geometry import Point
from compas.geometry import Polyline
from compas_occ.geometry import OCCNurbsCurve
from compas_view2.app import App

points1 = [Point(0, 0, 0), Point(1, 1, 0), Point(3, 0, 0)]
points2 = [Point(3, 0, 0), Point(4, -2, 0), Point(5, 0, 0)]

curve1 = OCCNurbsCurve.from_interpolation(points1)
curve2 = OCCNurbsCurve.from_interpolation(points2)

joined = curve1.joined(curve2)
curve1.join(curve2)

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

view.add(Polyline(curve1.locus()), linewidth=3, linecolor=(1, 0, 0))
view.add(Polyline(curve2.locus()), linewidth=3, linecolor=(0, 1, 0))
view.add(Polyline(joined.locus()), linewidth=3, linecolor=(0, 0, 1))

view.run()
