# type: ignore

from compas.geometry import Point
from compas.geometry import NurbsSurface
from compas_view2.app import App


points = [
    [Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0), Point(3, 0, 0)],
    [Point(0, 1, 0), Point(1, 1, 2), Point(2, 1, 2), Point(3, 1, 0)],
    [Point(0, 2, 0), Point(1, 2, 2), Point(2, 2, 2), Point(3, 2, 0)],
    [Point(0, 3, 0), Point(1, 3, 0), Point(2, 3, 0), Point(3, 3, 0)],
]

surface = NurbsSurface.from_points(points=points)

# ==============================================================================
# JSON Data
# ==============================================================================

string = surface.to_jsonstring(pretty=True)

print(string)

other = NurbsSurface.from_jsonstring(string)

print(surface == other)

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

u = surface.isocurve_u(0.5 * sum(surface.domain_u))
v = surface.isocurve_v(0.5 * sum(surface.domain_v))

view.add(u.to_polyline(), linewidth=1, linecolor=(0.3, 0.3, 0.3))
view.add(v.to_polyline(), linewidth=1, linecolor=(0.3, 0.3, 0.3))

for curve in surface.boundary():
    view.add(curve.to_polyline(), linewidth=2, linecolor=(0, 0, 0))

view.add(other)
view.run()
