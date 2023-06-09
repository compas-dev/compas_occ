from compas.geometry import Point, Vector, Plane
from compas.geometry import Box, Cylinder
from compas.geometry import Brep
from compas_view2.app import App
from compas_view2.objects import Collection

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

A = Brep.from_box(box)
B1 = Brep.from_cylinder(cx)
B2 = Brep.from_cylinder(cy)
B3 = Brep.from_cylinder(cz)

C = A - (B1 + B2 + B3)

# ==============================================================================
# Visualisation
# ==============================================================================

viewer = App(viewmode="ghosted", width=1600, height=900)
viewer.view.camera.rz = -30
viewer.view.camera.rx = -75
viewer.view.camera.distance = 7

viewer.add(C)

viewer.run()
