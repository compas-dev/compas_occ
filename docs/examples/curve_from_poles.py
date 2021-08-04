from compas.geometry import Point, Line, Polyline
from compas.utilities import pairwise
from compas_occ.geometry import BSplineCurve

from compas_view2.app import App
from compas_view2.objects import Collection

poles = [Point(0, 0, 0), Point(3, 6, 0), Point(6, -3, 3), Point(10, 0, 0)]

curve = BSplineCurve.from_parameters(
    poles=poles,
    knots=[0.0, 1.0],
    multiplicities=[4, 4],
    degree=3
)

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

view.add(Polyline(curve.locus()), linewidth=3)
view.add(Collection(curve.poles), size=20, color=(1, 0, 0))

for a, b in pairwise(poles):
    view.add(Line(a, b), linewidth=1, linecolor=(0.3, 0.3, 0.3))

view.run()
