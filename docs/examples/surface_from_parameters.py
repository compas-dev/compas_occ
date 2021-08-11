from compas.geometry import Point, Line
from compas.utilities import pairwise
from compas_occ.geometry import NurbsSurface

from compas_view2.app import App
from compas_view2.objects import Collection

points = [
    [Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0), Point(3, 0, 0)],
    [Point(0, 1, 0), Point(1, 1, 2), Point(2, 1, 2), Point(3, 1, 0)],
    [Point(0, 2, 0), Point(1, 2, 2), Point(2, 2, 2), Point(3, 2, 0)],
    [Point(0, 3, 0), Point(1, 3, 0), Point(2, 3, 0), Point(3, 3, 0)],
    [Point(0, 4, 0), Point(1, 4, 0), Point(2, 4, 0), Point(3, 4, 0)],
]

weights = [
    [1.0, 1.0, 1.0, 1.0],
    [1.0, 2.0, 2.0, 1.0],
    [1.0, 2.0, 2.0, 1.0],
    [1.0, 1.0, 1.0, 1.0],
    [1.0, 1.0, 1.0, 1.0],
]

surface = NurbsSurface.from_parameters(
    points=points,
    weights=weights,
    u_knots=[0.0, 1.0],
    v_knots=[0.0, 1.0, 2.0],
    u_mults=[4, 4],
    v_mults=[4, 1, 4],
    u_degree=3,
    v_degree=3,
)

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

view.add(surface.to_mesh(u=50))

view.run()
