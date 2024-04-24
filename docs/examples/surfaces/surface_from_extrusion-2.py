from compas.geometry import NurbsCurve
from compas.geometry import NurbsSurface
from compas.geometry import Point
from compas.geometry import Vector
from compas_viewer import Viewer

points = [Point(0, 0, 0), Point(0, -6, 3), Point(0, 2, 6), Point(0, -2, 9)]
curve = NurbsCurve.from_points(points)
vector = Vector(5, 0, 0)

surface = NurbsSurface.from_extrusion(curve, vector)

# =============================================================================
# Visualisation
# =============================================================================

viewer = Viewer()
# viewer.view.camera.position = [-7, -10, 6]
# viewer.view.camera.target = [2, 0, 5]

viewer.scene.add(curve.to_polyline(), linewidth=5, linecolor=(1, 0, 0))
viewer.scene.add(surface)
viewer.show()
