from compas.colors import Color
from compas.geometry import Bezier
from compas.geometry import NurbsCurve
from compas.geometry import Point
from compas.geometry import Polyline
from compas_viewer import Viewer

points = [Point(0, 0, 0), Point(1, 3, 0), Point(2, 0, 0)]
bezier = Bezier(points)

points = [Point(3, 0, 0), Point(4, 3, 0), Point(5, 0, 0)]

curve1 = NurbsCurve.from_parameters(
    points=points,
    weights=[1.0, 1.0, 1.0],
    knots=[0.0, 1.0],
    multiplicities=[3, 3],
    degree=2,
)

curve2 = NurbsCurve.from_parameters(
    points=points,
    weights=[1.0, 2.0, 1.0],
    knots=[0.0, 1.0],
    multiplicities=[3, 3],
    degree=2,
)

curve3 = NurbsCurve.from_parameters(
    points=points,
    weights=[1.0, 1.0, 1.0],
    knots=[0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
    multiplicities=[1, 1, 1, 1, 1, 1],
    degree=2,
)

# ==============================================================================
# Visualization
# ==============================================================================

viewer = Viewer()
viewer.renderer.view = "top"

viewer.scene.add(
    Polyline(bezier.points),
    show_points=True,
    pointsize=20,
    pointcolor=Color.red(),
    linewidth=1,
    linecolor=Color(0.3, 0.3, 0.3),
)
viewer.scene.add(bezier.to_polyline(), linewidth=5, linecolor=Color(0, 0, 0), show_points=False)

viewer.scene.add(
    Polyline(curve1.points),
    show_points=True,
    pointsize=20,
    pointcolor=Color.red(),
    linewidth=1,
    linecolor=Color(0.3, 0.3, 0.3),
)
viewer.scene.add(curve1, linewidth=5, linecolor=Color(0.0, 0.0, 0.0))
viewer.scene.add(curve2, linewidth=5, linecolor=Color(0.0, 1.0, 1.0))
viewer.scene.add(curve3, linewidth=5, linecolor=Color(0.0, 0.0, 1.0))

viewer.show()
