from compas.geometry import Point
from compas.geometry import Polyline
from compas_occ.geometry import NurbsSurface
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
for u in surface.u_space():
    u_curves.append(surface.u_isocurve(u))

v_curves = []
for v in surface.v_space():
    v_curves.append(surface.v_isocurve(v))

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

for curve in u_curves:
    view.add(Polyline(curve.locus()), linecolor=(1, 0, 0), linewidth=2)

for curve in v_curves:
    view.add(Polyline(curve.locus()), linecolor=(0, 1, 0), linewidth=2)

view.run()
