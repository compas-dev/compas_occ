from compas.geometry import Point, Line, Polyline

from compas_view2.app import App

from compas_occ.geometry import BSplineCurve
from compas_occ.geometry import BSplineSurface


points1 = []
points1.append(Point(-4, 0, 2))
points1.append(Point(-7, 2, 2))
points1.append(Point(-6, 3, 1))
points1.append(Point(-4, 3, -1))
points1.append(Point(-3, 5, -2))
spline1 = BSplineCurve.from_points(points1)

points2 = []
points2.append(Point(-4, 0, 2))
points2.append(Point(-2, 2, 0))
points2.append(Point(2, 3, -1))
points2.append(Point(3, 7, -2))
points2.append(Point(4, 9, -1))
spline2 = BSplineCurve.from_points(points2)

surface = BSplineSurface.from_fill(spline1, spline2)
line = Line(Point(0, 4, 0), Point(0, 4, 1))

mesh = surface.to_tesselation()
boundary = Polyline(mesh.vertices_attributes('xyz', keys=mesh.vertices_on_boundary()))

view = App()
view.add(mesh, show_edges=False)
view.add(boundary, linewidth=2)

for point in surface.intersections(line):
    view.add(point, size=10, color=(1, 0, 0))

view.run()
