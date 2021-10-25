from compas.geometry import Point, Polyline
from compas_occ.geometry import OCCNurbsCurve as NurbsCurve

from compas_view2.app import App

points = [Point(0, 0, 0), Point(3, 6, 0), Point(6, -3, 3), Point(10, 0, 0)]

curve = NurbsCurve.from_parameters(
    points=points,
    weights=[1.0, 1.0, 1.0, 1.0],
    knots=[0.0, 1.0],
    multiplicities=[4, 4],
    degree=3
)

print(curve)

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

view.add(Polyline(curve.locus()), linewidth=3)
view.add(Polyline(curve.points), show_points=True, pointsize=20, pointcolor=(1, 0, 0), linewidth=1, linecolor=(0.3, 0.3, 0.3))

view.run()
