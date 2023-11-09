# type: ignore

from compas.geometry import Point
from compas_occ.geometry import OCCNurbsSurface
from compas_view2.app import App


points = [
    [Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0), Point(3, 0, 0)],
    [Point(0, 1, 0), Point(1, 1, 2), Point(2, 1, 2), Point(3, 1, 0)],
    [Point(0, 2, 0), Point(1, 2, 2), Point(2, 2, 2), Point(3, 2, 0)],
    [Point(0, 3, 0), Point(1, 3, 0), Point(2, 3, 0), Point(3, 3, 0)],
]

surface = OCCNurbsSurface.from_points(points=points)

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

view.add(surface, show_lines=True, show_points=True)

view.run()
