from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import NurbsCurve
from compas_occ.geometry import OCCExtrusionSurface
from compas_view2.app import App

points = [Point(0, 0, 0), Point(0, -6, 3), Point(0, 2, 6), Point(0, -2, 9)]
curve = NurbsCurve.from_points(points)
vector = Vector(-1, 0, 0)

surface = OCCExtrusionSurface(curve, vector=vector)

viewer = App()
viewer.view.camera.position = [-5, -10, 7]
viewer.view.camera.target = [0, 0, 5]

viewer.add(curve.to_polyline(), linewidth=5, color=(1, 0, 0))
viewer.add(surface.to_mesh())
viewer.show()
