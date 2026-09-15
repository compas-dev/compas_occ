from compas_viewer import Viewer

import compas
from compas.geometry import Box
from compas.geometry import Circle
from compas.geometry import Cylinder
from compas.geometry import Frame
from compas.geometry import NurbsCurve
from compas.geometry import NurbsSurface
from compas.geometry import Plane
from compas.geometry import Point
from compas.geometry import Sphere
from compas.geometry import Vector
from compas_occ.brep import OCCBrep
from compas_occ.brep import OCCBrepEdge
from compas_occ.brep import OCCBrepFace
from compas_occ.brep import OCCBrepLoop


def brep_with_hole():
    points = [
        [Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0), Point(3, 0, 0)],
        [Point(0, 1, 0), Point(1, 1, 2), Point(2, 1, 2), Point(3, 1, 0)],
        [Point(0, 2, 0), Point(1, 2, 2), Point(2, 2, 2), Point(3, 2, 0)],
        [Point(0, 3, 0), Point(1, 3, 0), Point(2, 3, 0), Point(3, 3, 0)],
    ]
    surface = NurbsSurface.from_points(points=points)
    circle = Circle(
        0.5,
        frame=Frame(
            Point(1.5, 1.5, 1.5),
            Vector(1, 0, 0),
            Vector(0, 1, 0),
        ),
    )
    curve = NurbsCurve.from_circle(circle)
    edge = OCCBrepEdge.from_curve_and_surface(curve=curve, surface=surface)
    loop = OCCBrepLoop.from_edges([edge])
    face = OCCBrepFace.from_surface(surface)
    face.add_loop(loop)
    brep = OCCBrep.from_brepfaces([face])
    return brep


def brep_with_holes():
    circle1 = Circle(1.0, frame=Frame([2, 2, 0]))
    circle2 = Circle(2.0, frame=Frame([-2, -2, 0]))
    circle3 = Circle(0.5, frame=Frame([2, -2, 0]))

    loop1 = OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(circle1)])
    loop2 = OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(circle2)])
    loop3 = OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(circle3)])

    face = OCCBrepFace.from_plane(Plane.worldXY(), domain_u=(-5, 5), domain_v=(-5, 5))
    face.add_loops([loop1, loop2, loop3], reverse=True)

    brep = OCCBrep.from_brepfaces([face])
    return brep


def brep_from_booleans():
    R = 1.4

    box = Box(2 * R).to_brep()
    sphere = Sphere(radius=1.25 * R).to_brep()

    cylx = Cylinder(radius=0.7 * R, height=3 * R, frame=Frame.worldYZ()).to_brep()
    cyly = Cylinder(radius=0.7 * R, height=3 * R, frame=Frame.worldZX()).to_brep()
    cylz = Cylinder(radius=0.7 * R, height=3 * R, frame=Frame.worldXY()).to_brep()

    brep = OCCBrep.from_boolean_intersection(box, sphere)
    brep = OCCBrep.from_boolean_difference(brep, cylz)
    brep = OCCBrep.from_boolean_difference(brep, cylx)
    brep = OCCBrep.from_boolean_difference(brep, cyly)
    return brep


# =============================================================================
# Dump/Load
# =============================================================================

# brep = OCCBrep.from_box(Box(1))
# brep = OCCBrep.from_sphere(Sphere(1.0))
# brep = OCCBrep.from_cylinder(Cylinder(1.0, 2.0))
brep = brep_from_booleans()
# brep = brep_with_hole()
# brep = brep_with_holes()

brep: OCCBrep = compas.json_loads(compas.json_dumps(brep))  # type: ignore

# =============================================================================
# Viz
# =============================================================================

viewer = Viewer()
viewer.scene.add(brep)
viewer.show()
