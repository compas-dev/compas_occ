# type: ignore
# this should be included in the compas API
from compas.geometry import Brep
from compas.geometry import Circle
from compas.geometry import Frame
from compas.geometry import NurbsCurve
from compas.geometry import NurbsSurface
from compas.geometry import Point
from compas.geometry import Vector
from compas_occ.brep import OCCBrepEdge
from compas_occ.brep import OCCBrepFace
from compas_occ.brep import OCCBrepLoop
from compas_viewer import Viewer

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

# projected is still 3D
# embedded is 2D
# and the 2D curve should keep track of the embedding surface
curve = NurbsCurve.from_circle(circle)

edge = OCCBrepEdge.from_curve(curve=curve, surface=surface)
loop = OCCBrepLoop.from_edges([edge])

# perhaps this should be:
# face = OCCBrepFace()
# face.set_surface(surface)
# face.add_boundary(loop) => if the loop edges are not embedded in the surface, they should be
# face.add_hole(loop) => if the loop edges ...
face = OCCBrepFace.from_surface(surface)
face.add_loop(loop)

brep = Brep.from_brepfaces([face])

# =============================================================================
# Visualization
# =============================================================================

viewer = Viewer()
# viewer.scene.add(brep, linewidth=2)
viewer.show()
