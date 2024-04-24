from compas.geometry import Line
from compas.geometry import NurbsCurve
from compas.geometry import Point
from compas_viewer import Viewer

line = Line(Point(0, 0, 0), Point(3, 3, 0))
curve = NurbsCurve.from_line(line)

# ==============================================================================
# Visualisation
# ==============================================================================

viewer = Viewer()

viewer.scene.add(curve.to_polyline(), linewidth=3)
# viewer.scene.add(Collection(curve.points), pointsize=20, pointcolor=(1, 0, 0))

viewer.show()
