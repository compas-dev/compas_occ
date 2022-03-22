
from compas.geometry import NurbsCurve
from compas.geometry import NurbsSurface


from compas.geometry import Point
from compas.geometry import Polyline

from compas_view2.app import App

points1 = [Point(0, -10, 0), Point(1, -8, 0), Point(-1, -6, 0), Point(0, -4, 0)]
points2 = [Point(5, -10, 0), Point(4, -8, 0), Point(6, -6, 0), Point(5, -4, 0)]

nurbscurve1 = NurbsCurve.from_interpolation(points1)
nurbscurve2 = NurbsCurve.from_interpolation(points2)

nurbssurface_2curves = NurbsSurface.from_fill(nurbscurve1, nurbscurve2)

points3 = [Point(0, 0, 0), Point(1, 2, 0), Point(-1, 4, 0), Point(0, 6, 0)]
points4 = [Point(0, 6, 0), Point(3, 6, -1), Point(5, 6, 0)]
points5 = [Point(5, 6, 0), Point(4, 2, 0), Point(5, 0, 0)]
points6 = [Point(5, 0, 0), Point(2, -1, 1), Point(0, 0, 0)]

nurbscurve3 = NurbsCurve.from_interpolation(points3)
nurbscurve4 = NurbsCurve.from_interpolation(points4)
nurbscurve5 = NurbsCurve.from_interpolation(points5)
nurbscurve6 = NurbsCurve.from_interpolation(points6)

nurbssurface_4curves = NurbsSurface.from_fill(nurbscurve3, nurbscurve4, nurbscurve5, nurbscurve6, 'curved')


# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

view.add(Polyline(nurbscurve1.locus()), linewidth=3, linecolor=(1, 0, 0))
view.add(Polyline(nurbscurve2.locus()), linewidth=3, linecolor=(0, 1, 0))

view.add(Polyline(nurbscurve3.locus()), linewidth=3, linecolor=(1, 0, 0))
view.add(Polyline(nurbscurve4.locus()), linewidth=3, linecolor=(0, 1, 0))
view.add(Polyline(nurbscurve5.locus()), linewidth=3, linecolor=(1, 0, 1))
view.add(Polyline(nurbscurve6.locus()), linewidth=3, linecolor=(0, 0, 1))

view.add(nurbssurface_2curves.to_mesh(nu=10))
view.add(nurbssurface_4curves.to_mesh(nu=10))

view.run()
