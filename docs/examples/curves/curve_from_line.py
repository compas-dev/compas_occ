# type: ignore

from compas.geometry import Point
from compas.geometry import Line
from compas.geometry import NurbsCurve
from compas_view2.app import App
from compas_view2.objects import Collection


line = Line(Point(0, 0, 0), Point(3, 3, 0))
curve = NurbsCurve.from_line(line)

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

view.add(curve.to_polyline(), linewidth=3)
view.add(Collection(curve.points), pointsize=20, pointcolor=(1, 0, 0))

view.run()
