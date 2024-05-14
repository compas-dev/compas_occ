from compas.geometry import NurbsCurve
from compas.geometry import Point
from compas.geometry import Vector
from compas_occ.geometry import OCCRevolutionSurface
from compas_viewer import Viewer

points = [Point(0, 0, 0), Point(0, -6, 3), Point(0, 2, 6), Point(0, -2, 9)]
curve = NurbsCurve.from_points(points)
point = Point(0, 0, 0)
vector = Vector(0, 0, 1)

# TODO: TypeError: __init__() missing 1 required positional argument: 'occ_surface'
surface = OCCRevolutionSurface(curve, point=point, vector=vector)

# =============================================================================
# Visualisation
# =============================================================================

viewer = Viewer()
# viewer.renderer.camera.position = [-5, -10, 7]
# viewer.renderer.camera.target = [0, 0, 5]

viewer.scene.add(curve.to_polyline(), lineswidth=5, linecolor=(1, 0, 0))
viewer.scene.add(surface.to_mesh())
viewer.show()
