# type: ignore

from compas.geometry import Point
from compas.geometry import Vector
from compas_occ.geometry import OCCNurbsCurve
from compas_occ.geometry import OCCNurbsSurface
from compas_view2.app import App

points = [Point(0, 0, 0), Point(0, -6, 3), Point(0, 2, 6), Point(0, -2, 9)]
curve = OCCNurbsCurve.from_points(points)
vector = Vector(5, 0, 0)

surface = OCCNurbsSurface.from_extrusion(curve, vector)

viewer = App()
viewer.view.camera.position = [-7, -10, 6]
viewer.view.camera.target = [2, 0, 5]

viewer.add(curve.to_polyline(), linewidth=5, linecolor=(1, 0, 0))
viewer.add(surface)
viewer.show()
