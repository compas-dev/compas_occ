# type: ignore

from compas.geometry import Vector
from compas.geometry import Circle
from compas.geometry import NurbsCurve
from compas_occ.geometry import (
    OCCNurbsSurface as NurbsSurface,
)  # this should be added to the pluggable API
from compas_view2.app import App

curve = NurbsCurve.from_circle(Circle(2.0))

surface = NurbsSurface.from_extrusion(curve, Vector(0, 0, 5))

# =============================================================================
# Visualisation
# =============================================================================

viewer = App()
viewer.view.camera.position = [-5, -10, 4]
viewer.view.camera.target = [0, 0, 2]

viewer.add(curve.to_polyline(), linewidth=5, linecolor=(1, 0, 0))
viewer.add(surface)
viewer.show()
