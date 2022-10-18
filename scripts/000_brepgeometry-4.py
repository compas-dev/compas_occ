from compas.geometry import Point, Vector, Plane
from compas.geometry import Box, Cylinder

from compas_occ.geometry import OCCNurbsSurface
from compas_occ.brep import BRepEdge, BRepLoop, BRepFace, BRep
from compas_occ.conversions import compas_plane_from_occ_plane

from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
from OCC.Core.TopAbs import TopAbs_Orientation

from compas_occ.conversions.primitives import (
    compas_cylinder_from_occ_cylinder,
    compas_sphere_from_occ_sphere,
)


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

brep = A - (B1 + B2 + B3)

data = {"faces": []}

print(f"\nFaces ({len(brep.faces)})")
print("=" * 17)

for face in brep.faces:
    facedata = {"surface": None, "loops": []}

    if face.is_plane:
        surface = BRepAdaptor_Surface(face.occ_face).Plane()
        surfdata = compas_plane_from_occ_plane(surface)

    elif face.is_cylinder:
        surface = BRepAdaptor_Surface(face.occ_face).Cylinder()
        surfdata = compas_cylinder_from_occ_cylinder(surface)

    elif face.is_cone:
        surface = BRepAdaptor_Surface(face.occ_face).Cone()
        raise NotImplementedError

    elif face.is_sphere:
        surface = BRepAdaptor_Surface(face.occ_face).Sphere()
        surfdata = compas_sphere_from_occ_sphere(surface)

    elif face.is_torus:
        surface = BRepAdaptor_Surface(face.occ_face).Torus()
        raise NotImplementedError

    elif face.is_bezier:
        surface = BRepAdaptor_Surface(face.occ_face).Bezier()
        raise NotImplementedError

    elif face.is_bspline:
        surface = BRepAdaptor_Surface(face.occ_face).BSpline()
        surfdata = OCCNurbsSurface.from_occ(surface)

    else:
        print(face.type)
        raise NotImplementedError

    print("\nSurfaces")
    print(f"- {surface}")

    outer = face.loops[0]
    inner = face.loops[1:]

    loops = []

    print("\nOuter loop")

    loopdata = []

    for edge in outer.edges:
        if edge.is_line:
            curve = BRepAdaptor_Curve(edge.occ_edge).Line()

        elif edge.is_circle:
            curve = BRepAdaptor_Curve(edge.occ_edge).Circle()

        elif edge.is_ellipse:
            curve = BRepAdaptor_Curve(edge.occ_edge).Ellipse()

        elif edge.is_parabola:
            curve = BRepAdaptor_Curve(edge.occ_edge).Parabola()

        elif edge.is_hyperbola:
            curve = BRepAdaptor_Curve(edge.occ_edge).Hyperbola()

        elif edge.is_bezier:
            curve = BRepAdaptor_Curve(edge.occ_edge).Bezier()

        elif edge.is_bspline:
            curve = BRepAdaptor_Curve(edge.occ_edge).BSpline()

        else:
            print(edge.type)

        orientation = (
            "REVERSED"
            if edge.orientation == TopAbs_Orientation.TopAbs_REVERSED
            else "FORWARD"
        )
        print(f"- {curve} ({orientation})")

    print("\nInner loops")
    for loop in inner:
        for edge in loop.edges:
            if edge.is_line:
                curve = BRepAdaptor_Curve(edge.occ_edge).Line()
            elif edge.is_circle:
                curve = BRepAdaptor_Curve(edge.occ_edge).Circle()
            elif edge.is_ellipse:
                curve = BRepAdaptor_Curve(edge.occ_edge).Ellipse()
            elif edge.is_parabola:
                curve = BRepAdaptor_Curve(edge.occ_edge).Parabola()
            elif edge.is_hyperbola:
                curve = BRepAdaptor_Curve(edge.occ_edge).Hyperbola()
            elif edge.is_bezier:
                curve = BRepAdaptor_Curve(edge.occ_edge).Bezier()
            elif edge.is_bspline:
                try:
                    curve = BRepAdaptor_Curve(edge.occ_edge).BSpline()
                except Exception as e:
                    print(e)
            else:
                print(edge.type)

            orientation = (
                "REVERSED"
                if edge.orientation == TopAbs_Orientation.TopAbs_REVERSED
                else "FORWARD"
            )
            print(f"- {curve} ({orientation})")

        print()

    facedata["surface"] = surfdata
    facedata["loops"] = loops

    data["faces"].append(facedata)
