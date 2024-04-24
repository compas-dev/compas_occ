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
# viewer.view.camera.position = [-5, -10, 4]
# viewer.view.camera.target = [0, 0, 2]

viewer.scene.add(curve.to_polyline(), linewidth=5, linecolor=(1, 0, 0))
viewer.scene.add(surface)
viewer.show()
