import compas
from compas.geometry import Box
from compas.geometry import Sphere
from compas.geometry import Cylinder
from compas_occ.brep import BRep

from OCC.Core.BRepAdaptor import BRepAdaptor_Surface

box = Box.from_corner_corner_height([0, 0, 0], [1, 1, 0], 1)
brep = BRep.from_box(box)

sphere = Sphere([0, 0, 0], 1)
brep = BRep.from_sphere(sphere)

cylinder = Cylinder([([0, 0, 0], [0, 0, 1]), 1.0], 1.0)
brep = BRep.from_cylinder(cylinder)

print(len(brep.faces))

for face in brep.faces:
    print()
    if face.is_plane:
        plane = BRepAdaptor_Surface(face.occ_face).Plane()
        print(plane)
    elif face.is_cylinder:
        cylinder = BRepAdaptor_Surface(face.occ_face).Cylinder()
        print(cylinder)
    elif face.is_cone:
        cone = BRepAdaptor_Surface(face.occ_face).Cone()
        print(cone)
    elif face.is_sphere:
        sphere = BRepAdaptor_Surface(face.occ_face).Sphere()
        print(sphere)
    elif face.is_torus:
        torus = BRepAdaptor_Surface(face.occ_face).Torus()
        print(torus)
    elif face.is_bezier:
        bezier = BRepAdaptor_Surface(face.occ_face).Bezier()
        print(bezier)
    elif face.is_bspline:
        bspline = BRepAdaptor_Surface(face.occ_face).BSpline()
        print(bspline)
    else:
        raise NotImplementedError