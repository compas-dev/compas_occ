import random

from compas_viewer import Viewer

from compas.colors import Color
from compas.geometry import Point
from compas.geometry import Polyline
from compas.itertools import linspace
from compas.itertools import meshgrid
from compas_occ.geometry import OCCNurbsSurface

U = 10
V = 20

UU, VV = meshgrid(linspace(0.0, float(U), U + 1), linspace(0.0, float(V), V + 1))
surface = OCCNurbsSurface.from_points([[Point(u, v, 0.0) for u, v in zip(row_u, row_v)] for row_u, row_v in zip(UU, VV)])

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

viewer.scene.add(surface)

# control polygon

points = list(surface.points)
viewer.scene.add([Polyline(row) for row in points], linewidth=1, linecolor=Color(0.3, 0.3, 0.3))
viewer.scene.add([Polyline(col) for col in zip(*points)], linewidth=1, linecolor=Color(0.3, 0.3, 0.3))
viewer.scene.add(points, pointsize=10)

# isocurves

u_curves = []
for u in surface.space_u(53):
    u_curves.append(surface.isocurve_u(u).to_polyline())

v_curves = []
for v in surface.space_v(53):
    v_curves.append(surface.isocurve_v(v).to_polyline())

viewer.scene.add(u_curves, linecolor=Color(0.8, 0.8, 0.8), linewidth=3)
viewer.scene.add(v_curves, linecolor=Color(0.8, 0.8, 0.8), linewidth=3)

viewer.show()
