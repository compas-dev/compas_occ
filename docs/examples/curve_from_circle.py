from compas.geometry import Vector, Point, Plane
from compas.geometry import Polyline
from compas.geometry import Circle
from compas_occ.geometry import NurbsCurve
from compas_view2.app import App


circle = Circle(Plane(Point(0, 0, 0), Vector(0, 0, 1)), 1.0)
curve = NurbsCurve.from_circle(circle)

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

view.add(Polyline(curve.locus()), linewidth=3)
view.add(Polyline(curve.points), show_points=True, pointsize=20, pointcolor=(1, 0, 0), linewidth=1, linecolor=(0.3, 0.3, 0.3))

view.run()
