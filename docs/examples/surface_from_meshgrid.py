from compas.geometry import Point, Polyline
from compas.utilities import meshgrid, linspace
# from compas.geometry import NurbsSurface
from compas_occ.geometry import OCCNurbsSurface as NurbsSurface

from compas_view2.app import App

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
    view.add(Polyline(row), show_points=True, pointsize=20, pointcolor=(1, 0, 0), linewidth=2, linecolor=(0.3, 0.3, 0.3))

for col in zip(* surface.points):
    view.add(Polyline(col), show_points=True, pointsize=20, pointcolor=(1, 0, 0), linewidth=2, linecolor=(0.3, 0.3, 0.3))

view.add(surface.to_mesh(nu=100, nv=50))

view.run()
