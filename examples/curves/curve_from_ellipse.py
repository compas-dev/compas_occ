from compas_viewer import Viewer

from compas.colors import Color
from compas.geometry import Ellipse
from compas.geometry import NurbsCurve
from compas.geometry import Polyline

ellipse = Ellipse(2.0, 1.0)
curve = NurbsCurve.from_ellipse(ellipse)

# ==============================================================================
# Visualisation
# ==============================================================================

viewer = Viewer()
viewer.renderer.view = "top"

viewer.scene.add(curve, linewidth=3)
viewer.scene.add(
    Polyline(curve.points),
    show_points=True,
    pointsize=20,
    pointcolor=Color.red(),
    linewidth=1,
    linecolor=Color(0.3, 0.3, 0.3),
)

viewer.show()
