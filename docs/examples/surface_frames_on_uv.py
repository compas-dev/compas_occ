from compas.geometry import Point, Polyline
from compas_occ.geometry import NurbsCurve
from compas_occ.geometry import NurbsSurface
from compas.utilities import meshgrid, flatten

from compas_view2.app import App

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

surface = NurbsSurface.from_fill(spline1, spline2)

U, V = meshgrid(surface.u_space(15), surface.v_space(10), 'ij')

frames = [surface.frame_at(u, v) for u, v in zip(flatten(U[1:]), flatten(V))]

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

view.add(surface.to_tesselation(), show_edges=False)
view.add(Polyline(spline1.locus()), linewidth=2)
view.add(Polyline(spline2.locus()), linewidth=2)

for frame in frames:
    view.add(frame, size=0.1)

view.run()
