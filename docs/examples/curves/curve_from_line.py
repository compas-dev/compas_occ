from compas.colors import Color
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
viewer.renderer.view = "top"

viewer.scene.add(curve, linewidth=3)
viewer.scene.add(curve.points, pointsize=20, pointcolor=Color(1, 0, 0))

viewer.show()
