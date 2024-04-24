from compas.geometry import NurbsSurface
from compas.geometry import Point
from compas.geometry import Polyline
from compas.itertools import linspace
from compas.itertools import meshgrid
from compas_viewer import Viewer

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

# ==============================================================================
# Visualisation
# ==============================================================================

viewer = Viewer()

for row in surface.points:
    viewer.scene.add(
        Polyline(row),
        show_points=True,
        pointsize=20,
        pointcolor=(1, 0, 0),
        linewidth=2,
        linecolor=(0.3, 0.3, 0.3),
    )

for col in zip(*surface.points):
    viewer.scene.add(
        Polyline(col),
        show_points=True,
        pointsize=20,
        pointcolor=(1, 0, 0),
        linewidth=2,
        linecolor=(0.3, 0.3, 0.3),
    )

viewer.scene.add(surface.to_mesh(nu=100, nv=50))

viewer.show()
