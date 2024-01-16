# type: ignore

from compas.geometry import Line
from compas.geometry import Ellipse
from compas.utilities import pairwise
from compas.geometry import NurbsCurve
from compas_view2.app import App
from compas_view2.objects import Collection


ellipse = Ellipse(2.0, 1.0)
curve = NurbsCurve.from_ellipse(ellipse)

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

view.add(curve.to_polyline(), linewidth=3)
view.add(Collection(curve.points), pointsize=20, pointcolor=(1, 0, 0))

for a, b in pairwise(curve.points):
    view.add(Line(a, b), linewidth=1, linecolor=(0.3, 0.3, 0.3))

view.run()
