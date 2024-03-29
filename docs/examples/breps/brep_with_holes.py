# type: ignore
from compas.geometry import Frame, Plane, Circle
from compas_occ.brep import (
    OCCBrepEdge,
    OCCBrepLoop,
    OCCBrepFace,
)  # this should be included in the compas API
from compas.geometry import Brep
from compas_view2.app import App

circle1 = Circle(1.0, frame=Frame([2, 2, 0]))
circle2 = Circle(2.0, frame=Frame([-2, -2, 0]))
circle3 = Circle(0.5, frame=Frame([2, -2, 0]))

loop1 = OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(circle1)])
loop2 = OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(circle2)])
loop3 = OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(circle3)])

face = OCCBrepFace.from_plane(Plane.worldXY(), domain_u=(-5, 5), domain_v=(-5, 5))
face.add_loops([loop1, loop2, loop3], reverse=True)

brep = Brep.from_brepfaces([face])

# =============================================================================
# Visualization
# =============================================================================

viewer = App()
viewer.add(brep, linewidth=2)
viewer.show()
