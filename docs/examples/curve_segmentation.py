from compas.geometry import Point, Polyline
from compas_occ.geometry import NurbsCurve

from compas_view2.app import App


pointsA = [Point(0, 0, 0), Point(3, 6, 0), Point(6, -3, 3), Point(10, 0, 0)]
curveA = NurbsCurve.from_points(pointsA)

initial_curveA = curveA.copy()
curveA.segment(u=0.2, v=0.5)

print(curveA.domain)


pointsB = [Point(-6, -1, 0), Point(-3, 5, 0), Point(-0, -4, 3), Point(4, -1, 0)]
curveB = NurbsCurve.from_points(pointsB)

segment = curveB.segmented(u=0.2, v=0.5)

print(curveB.domain)
print(segment.domain)

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

view.add(Polyline(initial_curveA.locus()), linewidth=1, linecolor=(0.7, 0.7, 0.7))
view.add(Polyline(curveA.locus()), linewidth=4, linecolor=(1, 0, 0))

view.add(Polyline(curveB.locus()), linewidth=1, linecolor=(0, 0, 0))
view.add(Polyline(segment.locus()), linewidth=4, linecolor=(0, 1, 0))

view.run()
