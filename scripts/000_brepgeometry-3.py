from compas.geometry import Plane, Circle
from compas_occ.brep import BRepEdge, BRepLoop, BRepFace, BRep
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
from OCC.Core.TopAbs import TopAbs_Orientation


plane = Plane.worldXY()

circle1 = Circle(Plane([2, 2, 0], [0, 0, 1]), 1.0)
circle2 = Circle(Plane([-2, -2, 0], [0, 0, 1]), 2.0)
circle3 = Circle(Plane([2, -2, 0], [0, 0, 1]), 0.5)

loop1 = BRepLoop.from_edges([BRepEdge.from_circle(circle1)])
loop2 = BRepLoop.from_edges([BRepEdge.from_circle(circle2)])
loop3 = BRepLoop.from_edges([BRepEdge.from_circle(circle3)])

face = BRepFace.from_plane(plane, udomain=(-5, 5), vdomain=(-5, 5))
face.add_loops([loop1, loop2, loop3], reverse=True)

brep = BRep.from_faces([face])
brep.sew()
brep.fix()

print()
print(len(brep.faces))

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

    print(surface)

for face in brep.faces:
    print()
    print(len(face.loops))

    outer = face.loops[0]
    inner = face.loops[1:]

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

        print(TopAbs_Orientation(edge.orientation))
        print(curve)

    print()
    print(len(inner))
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

            print(TopAbs_Orientation(edge.orientation))
            print(curve)
