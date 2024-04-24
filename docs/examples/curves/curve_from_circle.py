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

viewer.scene.add(curve.to_polyline(), linewidth=3)
viewer.scene.add(
    Polyline(curve.points),
    show_points=True,
    pointsize=20,
    pointcolor=(1, 0, 0),
    linewidth=1,
    linecolor=(0.3, 0.3, 0.3),
)

viewer.show()
