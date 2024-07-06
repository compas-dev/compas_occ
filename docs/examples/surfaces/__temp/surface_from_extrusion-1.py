from compas.colors import Color
from compas.geometry import Circle
from compas.geometry import NurbsCurve
from compas.geometry import NurbsSurface
from compas.geometry import Vector
from compas_viewer import Viewer

curve = NurbsCurve.from_circle(Circle(2.0))

surface = NurbsSurface.from_extrusion(curve, Vector(0, 0, 5))

# =============================================================================
# Visualisation
# =============================================================================

viewer = Viewer()

viewer.renderer.camera.target = [0, 0, 2]
viewer.renderer.camera.position = [-5, -10, 4]

viewer.scene.add(curve, linewidth=5, linecolor=Color.red())
viewer.scene.add(surface)
viewer.show()
