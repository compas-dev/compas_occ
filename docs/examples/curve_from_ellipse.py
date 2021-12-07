from compas.geometry import Vector, Point, Line, Polyline, Ellipse, Plane
from compas.utilities import pairwise
from compas.geometry import NurbsCurve

from compas_view2.app import App
from compas_view2.objects import Collection

ellipse = Ellipse(Plane(Point(0, 0, 0), Vector(0, 0, 1)), 2.0, 1.0)
curve = NurbsCurve.from_ellipse(ellipse)

print(curve)

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

view.add(Polyline(curve.locus()), linewidth=3)
view.add(Collection(curve.points), size=20, color=(1, 0, 0))

for a, b in pairwise(curve.points):
    view.add(Line(a, b), linewidth=1, linecolor=(0.3, 0.3, 0.3))

view.run()
