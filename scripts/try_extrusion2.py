from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Translation
from compas.geometry import NurbsCurve
from compas.geometry import NurbsSurface
from compas_view2.app import App

points = [Point(0, 0, 0), Point(0, -6, 3), Point(0, 2, 6), Point(0, -2, 9)]
c1 = NurbsCurve.from_points(points)
c2 = c1.transformed(Translation.from_vector(Vector(10, 0, 0)))

surface = NurbsSurface.from_fill(c1, c2)

viewer = App()
viewer.view.camera.position = [-5, -10, 7]
viewer.view.camera.target = [0, 0, 5]

viewer.add(c1.to_polyline(), linewidth=5, color=(1, 0, 0))
viewer.add(c2.to_polyline(), linewidth=5, color=(1, 0, 0))
viewer.add(surface.to_mesh())
viewer.show()
