import os
from compas.geometry import Point
from compas_occ.geometry.curves.bspline import BSplineCurve

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, '__curve.stp')

points1 = []
points1.append(Point(-4, 0, 2))
points1.append(Point(-7, 2, 2))
points1.append(Point(-6, 3, 1))
points1.append(Point(-4, 3, -1))
points1.append(Point(-3, 5, -2))
spline1 = BSplineCurve.from_points(points1)

spline1.to_step(FILE)
