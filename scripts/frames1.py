from compas.geometry import Point, Polyline
from compas.utilities import meshgrid, flatten

from compas_view2.app import App

from compas_occ.geometry.curves import BSplineCurve
from compas_occ.geometry.surfaces import BSplineSurface

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

U, V = meshgrid(surface.uspace(30), surface.vspace(20), 'ij')

frames = [surface.frame_at(u, v) for u, v in zip(flatten(U[1:]), flatten(V))]

# ==============================================================================
# Viz
# ==============================================================================

mesh = surface.to_vizmesh()
boundary = Polyline(mesh.vertices_attributes('xyz', keys=mesh.vertices_on_boundary()))

view = App()
view.add(mesh)
view.add(boundary, linewidth=2)

for frame in frames:
    view.add(frame, size=0.1)

view.run()
