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

viewer.scene.add(
    Polyline(bezier.points),
    show_points=True,
    pointsize=20,
    pointcolor=(1, 0, 0),
    linewidth=1,
    linecolor=(0.3, 0.3, 0.3),
)
viewer.scene.add(bezier.to_polyline(), linewidth=5, linecolor=(0, 0, 0))

viewer.scene.add(
    Polyline(curve1.points),
    show_points=True,
    pointsize=20,
    pointcolor=(1, 0, 0),
    linewidth=1,
    linecolor=(0.3, 0.3, 0.3),
)
viewer.scene.add(curve1.to_polyline(), linewidth=5, linecolor=(0, 0, 0))
viewer.scene.add(curve2.to_polyline(), linewidth=5, linecolor=(0, 1, 1))
viewer.scene.add(curve3.to_polyline(), linewidth=5, linecolor=(0, 0, 1))

viewer.show()
