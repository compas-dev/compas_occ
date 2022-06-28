from compas.geometry import Point, Vector, Plane
from compas.geometry import Polyline
from compas.geometry import Box, Cylinder
from compas_occ.brep import BRep
from compas_view2.app import App


R = 1.4
P = Point(0, 0, 0)
X = Vector(1, 0, 0)
Y = Vector(0, 1, 0)
Z = Vector(0, 0, 1)
YZ = Plane(P, X)
ZX = Plane(P, Y)
XY = Plane(P, Z)

box = Box.from_width_height_depth(2 * R, 2 * R, 2 * R)
cx = Cylinder((YZ, 0.7 * R), 4 * R)
cy = Cylinder((ZX, 0.7 * R), 4 * R)
cz = Cylinder((XY, 0.7 * R), 4 * R)

A = BRep.from_box(box)
B1 = BRep.from_cylinder(cx)
B2 = BRep.from_cylinder(cy)
B3 = BRep.from_cylinder(cz)

# C = BRep.from_boolean_difference(
#     A,
#     BRep.from_boolean_union(
#         BRep.from_boolean_union(B1, B2),
#         B3
#     )
# )

C = A - (B1 + B2 + B3)

# ==============================================================================
# Visualisation
# ==============================================================================

# Currently, the viewer does not suppport BRep shapes.
# Therefore we have to convert the components of the BRep to something the viewer does understand.

mesh = C.to_tesselation()

lines = []
circles = []
ellipses = []

for edge in C.edges:
    if edge.is_line:
        lines.append(edge.to_line())
    elif edge.is_circle:
        circles.append(Polyline(edge.curve.locus()))
    elif edge.is_ellipse:
        ellipses.append(Polyline(edge.curve.locus()))
    else:
        raise NotImplementedError

viewer = App(viewmode="ghosted", width=1600, height=900)
viewer.view.camera.rz = -30
viewer.view.camera.rx = -75
viewer.view.camera.distance = 7

viewer.add(mesh, show_edges=False)

for line in lines:
    viewer.add(line, linewidth=2)

for circle in circles:
    viewer.add(circle, linewidth=2)

for ellipse in ellipses:
    viewer.add(ellipse, linewidth=2)

viewer.run()
