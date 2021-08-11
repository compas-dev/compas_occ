from compas.geometry import Point, Line
from compas.utilities import pairwise, meshgrid, linspace
from compas_occ.geometry import NurbsSurface

from compas_view2.app import App
from compas_view2.objects import Collection

UU, VV = meshgrid(linspace(0, 8, 9), linspace(0, 5, 6))

Z = 0.5

points = []
for i, (U, V) in enumerate(zip(UU, VV)):
    row = []
    for j, (u, v) in enumerate(zip(U, V)):
        if i == 0 or i == 5 or j == 0 or j == 8:
            z = 0.0
        elif i < 2 or i > 3:
            z = -1.0
        else:
            if j < 2 or j > 6:
                z = -1.0
            else:
                z = Z
        row.append(Point(u, v, z))
    points.append(row)

surface = NurbsSurface.from_points(points=points)

print(surface)

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

for row in surface.points:
    view.add(Collection(row), size=20, color=(1, 0, 0))

for row in surface.points:
    for a, b in pairwise(row):
        view.add(Line(a, b), linewidth=2, linecolor=(0.3, 0.3, 0.3))

for col in zip(* surface.points):
    for a, b in pairwise(col):
        view.add(Line(a, b), linewidth=2, linecolor=(0.3, 0.3, 0.3))

view.add(surface.to_mesh(u=100, v=50))

view.run()
