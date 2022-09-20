from compas.geometry import Point
from compas.geometry import Polyline
from compas_occ.geometry import OCCNurbsSurface
from compas_view2.app import App
from compas_view2.objects import Collection


points = [
    [Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0), Point(3, 0, 0), Point(4, 0, 0)],
    [Point(0, 1, 0), Point(1, 1, 2), Point(2, 1, 2), Point(3, 1, 0), Point(4, 1, 0)],
    [Point(0, 2, 0), Point(1, 2, 2), Point(2, 2, 2), Point(3, 2, 0), Point(4, 2, 0)],
    [Point(0, 3, 0), Point(1, 3, 0), Point(2, 3, 0), Point(3, 3, 0), Point(4, 3, 0)],
]

surface = OCCNurbsSurface.from_points(points=points)

# ==============================================================================
# Points over UV space
# ==============================================================================

spacepoints = surface.xyz(nu=50, nv=10)

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

for row in surface.points:
    view.add(
        Polyline(row),
        show_points=True,
        pointsize=20,
        pointcolor=(1, 0, 0),
        linewidth=2,
        linecolor=(1.0, 0.5, 0.5),
    )

for col in zip(*surface.points):
    view.add(
        Polyline(col),
        show_points=True,
        pointsize=20,
        pointcolor=(1, 0, 0),
        linewidth=2,
        linecolor=(0.5, 1.0, 0.5),
    )

view.add(surface.to_mesh(), show_lines=False)

view.add(Collection(spacepoints))

view.run()
