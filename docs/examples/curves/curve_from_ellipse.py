from compas.colors import Color
from compas.geometry import Ellipse
from compas.geometry import Line
from compas.geometry import NurbsCurve
from compas.itertools import pairwise
from compas_viewer import Viewer

ellipse = Ellipse(2.0, 1.0)
curve = NurbsCurve.from_ellipse(ellipse)

# ==============================================================================
# Visualisation
# ==============================================================================

viewer = Viewer()

viewer.scene.add(curve.to_polyline(), lineswidth=3, show_points=False)
# viewer.scene.add(Collection(curve.points), pointsize=20, pointcolor=(1, 0, 0))

for a, b in pairwise(curve.points):
    viewer.scene.add(Line(a, b), lineswidth=1, linecolor=Color(0.3, 0.3, 0.3))

viewer.show()
