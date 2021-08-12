import random

from OCC.Core.gp import gp_Pnt

from compas.geometry import Polyline
from compas_occ.geometry import NurbsSurface

from compas_view2.app import App

U = 10
V = 10

surface = NurbsSurface.from_meshgrid(nu=U, nv=V)

print(surface)

# ==============================================================================
# Update
# ==============================================================================

for u in range(2, U + 1):
    for v in range(2, V + 1):
        pole = surface.occ_surface.Pole(u, v)
        surface.occ_surface.SetPole(u, v, gp_Pnt(pole.X(), pole.Y(), random.choice([+1, -1]) * random.random()))

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

for row in surface.points:
    view.add(Polyline(row), show_points=True, pointsize=20, pointcolor=(1, 0, 0), linewidth=2, linecolor=(0.3, 0.3, 0.3))

for col in zip(* surface.points):
    view.add(Polyline(col), show_points=True, pointsize=20, pointcolor=(1, 0, 0), linewidth=2, linecolor=(0.3, 0.3, 0.3))

view.add(surface.to_mesh(u=100, v=50))

view.run()
