from compas.geometry import Point, Vector, Plane
from compas.geometry import Box, Cylinder
from compas_occ.brep import BRepEdge, BRepLoop, BRepFace, BRep
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
from OCC.Core.TopAbs import TopAbs_Orientation


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

print(f"\nFaces ({len(brep.faces)})")
print("=" * 17)

for face in brep.faces:
    if face.is_plane:
        surface = BRepAdaptor_Surface(face.occ_face).Plane()
    elif face.is_cylinder:
        surface = BRepAdaptor_Surface(face.occ_face).Cylinder()
    elif face.is_cone:
        surface = BRepAdaptor_Surface(face.occ_face).Cone()
    elif face.is_sphere:
        surface = BRepAdaptor_Surface(face.occ_face).Sphere()
    elif face.is_torus:
        surface = BRepAdaptor_Surface(face.occ_face).Torus()
    elif face.is_bezier:
        surface = BRepAdaptor_Surface(face.occ_face).Bezier()
    elif face.is_bspline:
        surface = BRepAdaptor_Surface(face.occ_face).BSpline()
    else:
        print(face.type)

    print("\nSurfaces")
    print(f"- {surface}")

    outer = face.loops[0]
    inner = face.loops[1:]

    print("\nOuter loop")
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
