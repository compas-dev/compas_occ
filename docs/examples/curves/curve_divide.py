from compas_viewer import Viewer

from compas.geometry import Point
from compas.itertools import pairwise
from compas_occ.geometry import OCCNurbsCurve

points = [Point(0, 0, 0), Point(3, -6, 0), Point(6, 2, 0), Point(9, -2, 0)]
curve = OCCNurbsCurve.from_points(points)

N = 10
params, points = curve.divide_by_count(N, return_points=True)

for u, v in pairwise(params):
    segment = curve.segmented(u, v)
    print(segment.length)

# =============================================================================
# Visualization
# =============================================================================

viewer = Viewer()
viewer.renderer.view = "top"

viewer.scene.add(curve, linewidth=2)
viewer.scene.add(points, pointsize=20)
viewer.show()
