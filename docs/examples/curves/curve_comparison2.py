from compas.colors import Color
from compas.geometry import Bezier
from compas.geometry import Point
from compas.geometry import Polyline
from compas_occ.geometry import OCCNurbsCurve
from compas_viewer import Viewer

points = [Point(0, 0, 0), Point(1, 2, 0), Point(2, -2, 0), Point(3, 0, 0)]
bezier = Bezier(points)

points = [Point(4, 0, 0), Point(5, 2, 0), Point(6, -2, 0), Point(7, 0, 0)]

curve1 = OCCNurbsCurve.from_parameters(
    points=points,
    weights=[1.0, 1.0, 1.0, 1.0],
    knots=[0.0, 1.0],
    multiplicities=[4, 4],
    degree=3,
)

curve2 = OCCNurbsCurve.from_parameters(
    points=points,
    weights=[1.0, 2.0, 2.0, 1.0],
    knots=[0.0, 1.0],
    multiplicities=[4, 4],
    degree=3,
)

curve3 = OCCNurbsCurve.from_parameters(
    points=points,
    weights=[1.0, 1.0, 1.0, 1.0],
    knots=[0.0, 1 / 3, 2 / 3, 1.0],
    multiplicities=[3, 1, 1, 3],
    degree=3,
)

curve4 = OCCNurbsCurve.from_parameters(
    points=points,
    weights=[1.0, 1.0, 1.0, 1.0],
    knots=[0.0, 1 / 5, 2 / 5, 3 / 5, 4 / 5, 1.0],
    multiplicities=[2, 1, 1, 1, 1, 2],
    degree=3,
)

curve5 = OCCNurbsCurve.from_parameters(
    points=points,
    weights=[1.0, 1.0, 1.0, 1.0],
    knots=[0.0, 1 / 7, 2 / 7, 3 / 7, 4 / 7, 5 / 7, 6 / 7, 1.0],
    multiplicities=[1, 1, 1, 1, 1, 1, 1, 1],
    degree=3,
)

curve6 = OCCNurbsCurve.from_parameters(
    points=points,
    weights=[1.0, 1.0, 1.0, 1.0],
    knots=[0.0, 0.5, 1.0],
    multiplicities=[3, 1, 3],
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
viewer.scene.add(bezier.to_polyline(), linewidth=5, linecolor=Color(0, 0, 0))

viewer.scene.add(
    Polyline(curve1.points),
    show_points=True,
    pointsize=20,
    pointcolor=Color.red(),
    linewidth=1,
    linecolor=Color(0.3, 0.3, 0.3),
)
viewer.scene.add(curve1, linewidth=5, linecolor=Color(0, 0, 0))
viewer.scene.add(curve2, linewidth=3, linecolor=Color.blue())
viewer.scene.add(curve3, linewidth=3, linecolor=Color(0.2, 0.2, 1.0))
viewer.scene.add(curve4, linewidth=3, linecolor=Color(0.4, 0.4, 1.0))
viewer.scene.add(curve5, linewidth=3, linecolor=Color(0.6, 0.6, 1.0))
viewer.scene.add(curve6, linewidth=3, linecolor=Color(0.8, 0.8, 1.0))

viewer.show()
