from compas_viewer import Viewer

from compas.geometry import NurbsCurve
from compas.geometry import Point
from compas.itertools import pairwise

points = [Point(0, 0, 0), Point(3, -6, 0), Point(6, 2, 0), Point(9, -2, 0)]
curve = NurbsCurve.from_points(points)

N = 10
params, points = curve.divide(N, return_points=True)  # type: ignore

for u, v in pairwise(params):
    segment = curve.segmented(u, v)
    print(segment.length())

# =============================================================================
# Visualization
# =============================================================================

viewer = Viewer()
viewer.renderer.view = "top"

viewer.scene.add(curve, linewidth=2)
viewer.scene.add(points, pointsize=20)
viewer.show()
