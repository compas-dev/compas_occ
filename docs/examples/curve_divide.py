from compas.utilities import pairwise
from compas.geometry import Point
from compas_occ.geometry import OCCNurbsCurve
from compas_view2.app import App

points = [Point(0, 0, 0), Point(3, -6, 0), Point(6, 2, 0), Point(9, -2, 0)]
curve = OCCNurbsCurve.from_points(points)

N = 10
params, points = curve.divide(N, return_points=True)

for u, v in pairwise(params):
    segment = curve.segmented(u, v)
    print(segment.length())

viewer = App()
viewer.add(curve.to_polyline())
for point in points:
    viewer.add(point)
viewer.show()
