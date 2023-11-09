# type: ignore

from compas.geometry import Polyline
from compas.geometry import Circle
from compas_occ.geometry import OCCNurbsCurve
from compas_view2.app import App


circle = Circle(1.0)
curve = OCCNurbsCurve.from_circle(circle)

# ==============================================================================
# Visualisation
# ==============================================================================

view = App()

view.add(curve.to_polyline(), linewidth=3)
view.add(
    Polyline(curve.points),
    show_points=True,
    pointsize=20,
    pointcolor=(1, 0, 0),
    linewidth=1,
    linecolor=(0.3, 0.3, 0.3),
)

view.run()
