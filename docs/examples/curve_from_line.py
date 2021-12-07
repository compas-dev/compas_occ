from compas.geometry import Point, Line, Polyline
from compas.geometry import NurbsCurve

from compas_view2.app import App
from compas_view2.objects import Collection

line = Line(Point(0, 0, 0), Point(3, 3, 0))
curve = NurbsCurve.from_line(line)

print(curve)

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

view.add(Polyline(curve.locus()), linewidth=3)
view.add(Collection(curve.points), size=20, color=(1, 0, 0))

view.run()
