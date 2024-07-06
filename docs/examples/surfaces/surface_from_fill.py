from compas.colors import Color
from compas.geometry import NurbsCurve
from compas.geometry import NurbsSurface
from compas.geometry import Point
from compas_viewer import Viewer

points1 = [Point(0, -10, 0), Point(1, -8, 0), Point(-1, -6, 0), Point(0, -4, 0)]
points2 = [Point(5, -10, 0), Point(4, -8, 0), Point(6, -6, 0), Point(5, -4, 0)]

nurbscurve1 = NurbsCurve.from_interpolation(points1)
nurbscurve2 = NurbsCurve.from_interpolation(points2)

nurbssurface_2curves = NurbsSurface.from_fill(nurbscurve1, nurbscurve2)

points3 = [Point(0, 0, 0), Point(1, 2, 0), Point(-1, 4, 0), Point(0, 6, 0)]
points4 = [Point(0, 6, 0), Point(3, 6, -1), Point(5, 6, 0)]
points5 = [Point(5, 6, 0), Point(4, 2, 0), Point(5, 0, 0)]
points6 = [Point(5, 0, 0), Point(2, -1, 1), Point(0, 0, 0)]

nurbscurve3 = NurbsCurve.from_interpolation(points3)
nurbscurve4 = NurbsCurve.from_interpolation(points4)
nurbscurve5 = NurbsCurve.from_interpolation(points5)
nurbscurve6 = NurbsCurve.from_interpolation(points6)

nurbssurface_4curves = NurbsSurface.from_fill(
    nurbscurve3,
    nurbscurve4,
    nurbscurve5,
    nurbscurve6,
    style="curved",
)

# ==============================================================================
# Visualisation
# ==============================================================================

viewer = Viewer()

viewer.scene.add(nurbscurve1, linewidth=3, linecolor=Color(1, 0, 0))
viewer.scene.add(nurbscurve2, linewidth=3, linecolor=Color(0, 1, 0))

viewer.scene.add(nurbscurve3, linewidth=3, linecolor=Color(1, 0, 0))
viewer.scene.add(nurbscurve4, linewidth=3, linecolor=Color(0, 1, 0))
viewer.scene.add(nurbscurve5, linewidth=3, linecolor=Color(1, 0, 1))
viewer.scene.add(nurbscurve6, linewidth=3, linecolor=Color(0, 0, 1))

viewer.scene.add(nurbssurface_2curves, show_lines=False)
viewer.scene.add(nurbssurface_4curves, show_lines=False)

viewer.show()
