from compas.geometry import Point, Vector, Plane
from compas.geometry import Box
from compas.geometry import Sphere
from compas.geometry import Cylinder
from compas_occ.brep.brep import BRep
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
sphere = Sphere([0, 0, 0], 1.25 * R)

cylx = Cylinder((YZ, 0.7 * R), 4 * R)
cyly = Cylinder((ZX, 0.7 * R), 4 * R)
cylz = Cylinder((XY, 0.7 * R), 4 * R)

A = BRep.from_box(box)
B = BRep.from_sphere(sphere)

C = BRep.from_cylinder(cylx)
D = BRep.from_cylinder(cyly)
E = BRep.from_cylinder(cylz)

F = BRep.from_boolean_difference(
    BRep.from_boolean_intersection(A, B),
    BRep.from_boolean_union(BRep.from_boolean_union(C, D), E),
)

# ==============================================================================
# Visualisation
# ==============================================================================

viewer = App()
viewer.add(F.to_tesselation())
viewer.run()
