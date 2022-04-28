from compas.geometry import Point
from compas.geometry import NurbsCurve
from compas_view2.app import App

points = [Point(0, 0, 0), Point(3, -6, 0), Point(6, 2, 0), Point(9, -2, 0)]
curve = NurbsCurve.from_points(points)

N = 10
params = curve.divide(N)
points = [curve.point_at(t) for t in params]

viewer = App()
viewer.add(curve.to_polyline())
for point in points:
    viewer.add(point)
viewer.show()
