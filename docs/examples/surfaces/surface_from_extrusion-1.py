# type: ignore

from compas.geometry import Vector
from compas.geometry import Circle
from compas_occ.geometry import OCCNurbsCurve
from compas_occ.geometry import OCCNurbsSurface
from compas_view2.app import App

curve = OCCNurbsCurve.from_circle(Circle(2.0))

surface = OCCNurbsSurface.from_extrusion(curve, Vector(0, 0, 5))

viewer = App()
viewer.view.camera.position = [-5, -10, 4]
viewer.view.camera.target = [0, 0, 2]

viewer.add(curve.to_polyline(), linewidth=5, linecolor=(1, 0, 0))
viewer.add(surface)
viewer.show()
