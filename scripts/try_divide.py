from compas.geometry import Point
from compas.geometry import NurbsCurve
from compas_view2.app import App

from OCC.Core.GCPnts import GCPnts_AbscissaPoint
from OCC.Core.GeomAdaptor import GeomAdaptor_Curve

points = [Point(0, 0, 0), Point(3, -6, 0), Point(6, 2, 0), Point(9, -2, 0)]
curve = NurbsCurve.from_points(points)

N = 10
L = curve.length()
l = L / N
t = 0

points = [curve.start]
for _ in range(N - 1):
    a = GCPnts_AbscissaPoint(GeomAdaptor_Curve(curve.occ_curve), l, t)
    if not a.IsDone():
        raise Exception
    t = a.Parameter()
    point = curve.point_at(t)
    points.append(point)
points.append(curve.end)

viewer = App()
viewer.add(curve.to_polyline())
for point in points:
    viewer.add(point)
viewer.show()
