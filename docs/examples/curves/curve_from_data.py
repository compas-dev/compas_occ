from compas.geometry import NurbsCurve
from compas.geometry import Point
from compas.geometry import Polyline
from compas_viewer import Viewer

points = [Point(0, 0, 0), Point(3, 6, 0), Point(6, -3, 3), Point(10, 0, 0)]

curve = NurbsCurve.from_points(points)

data = curve.data

# ==============================================================================
# Visualisation
# ==============================================================================

viewer = Viewer()

viewer.scene.add(curve.to_polyline(), linewidth=3)  # type: ignore

viewer.scene.add(
    Polyline(curve.points),
    show_points=True,
    pointsize=20,
    pointcolor=(1, 0, 0),  # type: ignore
    linewidth=1,
    linecolor=(0.3, 0.3, 0.3),  # type: ignore
)  # type: ignore

viewer.show()
