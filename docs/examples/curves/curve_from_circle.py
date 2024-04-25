from compas.colors import Color
from compas.geometry import Circle
from compas.geometry import NurbsCurve
from compas.geometry import Polyline
from compas_viewer import Viewer

circle = Circle(1.0)
curve = NurbsCurve.from_circle(circle)

# ==============================================================================
# Visualisation
# ==============================================================================

viewer = Viewer()

viewer.scene.add(curve.to_polyline(), lineswidth=3, show_points=False)
viewer.scene.add(
    Polyline(curve.points),
    show_points=True,
    pointsize=20,
    pointcolor=Color.red(),
    lineswidth=1,
    linecolor=Color(0.3, 0.3, 0.3),
)

viewer.show()
