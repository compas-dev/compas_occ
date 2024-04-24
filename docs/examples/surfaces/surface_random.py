import random

from compas.geometry import NurbsSurface
from compas.geometry import Polyline
from compas_viewer import Viewer

U = 10
V = 20

surface = NurbsSurface.from_meshgrid(nu=U, nv=V)

# ==============================================================================
# Update
# ==============================================================================

for u in range(1, U):
    for v in range(1, V):
        point = surface.points[u, v]
        point.z = random.choice([+1, -1]) * random.random()
        surface.points[u, v] = point

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

viewer.scene.add(surface.to_mesh(nu=100, nv=100))

viewer.show()
