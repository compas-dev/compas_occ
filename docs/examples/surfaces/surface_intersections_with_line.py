from math import radians

from compas.colors import Color
from compas.geometry import Line
from compas.geometry import NurbsSurface
from compas.geometry import Point
from compas.geometry import Polyline
from compas.geometry import Rotation
from compas.geometry import Vector
from compas.geometry import centroid_points_xy
from compas.itertools import flatten
from compas_viewer import Viewer

points = [
    [Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0), Point(3, 0, 0)],
    [Point(0, 1, 0), Point(1, 1, 2), Point(2, 1, 2), Point(3, 1, 0)],
    [Point(0, 2, 0), Point(1, 2, 2), Point(2, 2, 2), Point(3, 2, 0)],
    [Point(0, 3, 0), Point(1, 3, 0), Point(2, 3, 0), Point(3, 3, 0)],
]

surface = NurbsSurface.from_points(points=points)

# ==============================================================================
# Intersections
# ==============================================================================

base = Point(*centroid_points_xy(list(flatten(points))))
line = Line(base, base + Vector(0, 0, 1))

Ry = Rotation.from_axis_and_angle(Vector.Yaxis(), radians(30), point=base)
line.transform(Ry)

lines = []
for i in range(30):
    Rz = Rotation.from_axis_and_angle(Vector.Zaxis(), radians(i * 360 / 30), point=base)
    lines.append(line.transformed(Rz))

intersections = []
for line in lines:
    x = surface.intersections_with_line(line)
    if x:
        intersections.append(x[0])

# ==============================================================================
# Visualisation
# ==============================================================================

viewer = Viewer(rendermode="ghosted")

viewer.scene.add(surface)
viewer.scene.add(intersections, pointsize=10, pointcolor=Color.blue())
for x in intersections:
    viewer.scene.add(Line(base, base + (x - base).scaled(1.2)), linewidth=1, linecolor=Color.blue())

# control polygon

points = list(surface.points)
viewer.scene.add([Polyline(row) for row in points], linewidth=1, linecolor=Color(0.3, 0.3, 0.3))
viewer.scene.add([Polyline(col) for col in zip(*points)], linewidth=1, linecolor=Color(0.3, 0.3, 0.3))
viewer.scene.add(points, pointsize=10)

# isocurves

u_curves = []
for u in surface.space_u(7):  # type: ignore
    u_curves.append(surface.isocurve_u(u).to_polyline())

v_curves = []
for v in surface.space_v(7):  # type: ignore
    v_curves.append(surface.isocurve_v(v).to_polyline())

viewer.scene.add(u_curves, linecolor=Color(0.8, 0.8, 0.8), linewidth=3)
viewer.scene.add(v_curves, linecolor=Color(0.8, 0.8, 0.8), linewidth=3)

viewer.show()
