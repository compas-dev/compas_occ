# type: ignore

from compas.geometry import Point
from compas.geometry import NurbsSurface
from compas_view2.app import App


points = [
    [Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0), Point(3, 0, 0), Point(4, 0, 0)],
    [Point(0, 1, 0), Point(1, 1, 2), Point(2, 1, 2), Point(3, 1, 0), Point(4, 1, 0)],
    [Point(0, 2, 0), Point(1, 2, 2), Point(2, 2, 2), Point(3, 2, 0), Point(4, 2, 0)],
    [Point(0, 3, 0), Point(1, 3, 0), Point(2, 3, 0), Point(3, 3, 0), Point(4, 3, 0)],
]

surface = NurbsSurface.from_points(points=points)

# ==============================================================================
# Isocurves
# ==============================================================================

u_curves = []
for u in surface.space_u(5):
    u_curves.append(surface.isocurve_u(u))

v_curves = []
for v in surface.space_v(10):
    v_curves.append(surface.isocurve_v(v))

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

for curve in u_curves:
    view.add(curve.to_polyline(), linecolor=(1, 0, 0), linewidth=2)

for curve in v_curves:
    view.add(curve.to_polyline(), linecolor=(0, 1, 0), linewidth=2)

view.run()
