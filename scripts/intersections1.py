from compas.geometry import Point, Polyline

from compas_view2.app import App

from compas_occ.geometry.curves import BSplineCurve
from compas_occ.geometry.surfaces import BSplineSurface

from compas_occ.interop.primitives import compas_point_from_occ_point

from OCC.Core.gp import gp_Pnt, gp_Dir
from OCC.Core.Geom import Geom_Line
from OCC.Core.GeomAPI import GeomAPI_IntCS

Point.from_occ = classmethod(compas_point_from_occ_point)


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
line = Geom_Line(gp_Pnt(0, 4, 0), gp_Dir(0, 0, 1))

# ==============================================================================
# Intersection
# ==============================================================================

intersection = GeomAPI_IntCS(line, surface.occ_surface)

pnt = intersection.Point(1)
point = Point.from_occ(pnt)

# ==============================================================================
# Viz
# ==============================================================================

mesh = surface.to_vizmesh()
boundary = Polyline(mesh.vertices_attributes('xyz', keys=mesh.vertices_on_boundary()))

view = App()
view.add(mesh)
view.add(boundary, linewidth=2)
view.add(point, size=10, color=(1, 0, 0))
view.run()
