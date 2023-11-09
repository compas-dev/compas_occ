# type: ignore

from compas.geometry import Point
from compas.geometry import NurbsCurve
from compas_view2.app import App


points = [Point(0, 0, 0), Point(3, 0, 2), Point(6, 0, -3), Point(8, 0, 0)]
curve = NurbsCurve.from_interpolation(points)

point = Point(2, -1, 0)
closest, t = curve.closest_point(point, return_parameter=True)

view = App()

view.add(curve.to_polyline(), linewidth=3)
view.add(point, pointcolor=(0, 0, 1))
view.add(closest, pointcolor=(1, 0, 0))

view.run()
