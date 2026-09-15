from compas_viewer import Viewer

from compas.colors import Color
from compas.geometry import Circle
from compas.geometry import NurbsCurve
from compas.geometry import Polyline

circle = Circle(1.0)
curve = NurbsCurve.from_circle(circle)

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
