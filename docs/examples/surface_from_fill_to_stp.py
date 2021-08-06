import os
from compas.geometry import Point
from compas_occ.geometry import NurbsCurve
from compas_occ.geometry import BSplineSurface

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, 'surface.stp')

points1 = []
points1.append(Point(-4, 0, 2))
points1.append(Point(-7, 2, 2))
points1.append(Point(-6, 3, 1))
points1.append(Point(-4, 3, -1))
points1.append(Point(-3, 5, -2))
spline1 = NurbsCurve.from_interpolation(points1)

points2 = []
points2.append(Point(-4, 0, 2))
points2.append(Point(-2, 2, 0))
points2.append(Point(2, 3, -1))
points2.append(Point(3, 7, -2))
points2.append(Point(4, 9, -1))
spline2 = NurbsCurve.from_interpolation(points2)

surface = BSplineSurface.from_fill(spline1, spline2)
surface.to_step(FILE)
