from compas.geometry import Brep
from compas.geometry import Circle
from compas.geometry import Frame
from compas.geometry import Plane
from compas_occ.brep import OCCBrepEdge
from compas_occ.brep import OCCBrepFace
from compas_occ.brep import OCCBrepLoop
from compas_viewer import Viewer

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

viewer = Viewer()
viewer.scene.add(brep, linewidth=2, show_point=False)
viewer.show()
