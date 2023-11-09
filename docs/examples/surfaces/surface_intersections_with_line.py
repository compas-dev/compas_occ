# type: ignore

from math import radians
from compas.geometry import Point, Vector, Line, Polyline
from compas.geometry import Rotation
from compas.geometry import centroid_points_xy
from compas.utilities import flatten
from compas_occ.geometry import OCCNurbsSurface

from compas_view2.app import App
from compas_view2.objects import Collection

points = [
    [Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0), Point(3, 0, 0)],
    [Point(0, 1, 0), Point(1, 1, 2), Point(2, 1, 2), Point(3, 1, 0)],
    [Point(0, 2, 0), Point(1, 2, 2), Point(2, 2, 2), Point(3, 2, 0)],
    [Point(0, 3, 0), Point(1, 3, 0), Point(2, 3, 0), Point(3, 3, 0)],
]

surface = OCCNurbsSurface.from_points(points=points)

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

view = App(viewmode="ghosted")

for row in surface.points:
    view.add(
        Polyline(row),
        show_points=True,
        pointsize=20,
        pointcolor=(1, 0, 0),
        linewidth=2,
        linecolor=(0.3, 0.3, 0.3),
    )

for col in zip(*surface.points):
    view.add(
        Polyline(col),
        show_points=True,
        pointsize=20,
        pointcolor=(1, 0, 0),
        linewidth=2,
        linecolor=(0.3, 0.3, 0.3),
    )

view.add(Collection(intersections), pointsize=30, pointcolor=(0, 0, 1))

for x in intersections:
    view.add(
        Line(base, base + (x - base).scaled(1.2)), linewidth=1, linecolor=(0, 0, 1)
    )

view.add(surface)

view.run()
