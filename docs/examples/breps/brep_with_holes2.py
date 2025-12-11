from compas_viewer.viewer import Viewer

from compas.geometry import Brep
from compas.geometry import Circle
from compas.geometry import Frame
from compas.geometry import Polygon
from compas_occ.brep import OCCBrepFace
from compas_occ.brep import OCCBrepLoop

circle1 = Circle(1.0, frame=Frame([2, 2, 0]))
circle2 = Circle(2.0, frame=Frame([-2, -2, 0]))
circle3 = Circle(0.5, frame=Frame([2, -2, 0]))

loop1 = OCCBrepLoop.from_polygon(circle1.to_polygon(32))
loop2 = OCCBrepLoop.from_polygon(circle2.to_polygon(8))
loop3 = OCCBrepLoop.from_polygon(circle3.to_polygon(4))

polygon = Polygon.from_sides_and_radius_xy(5, 10.0)
face = OCCBrepFace.from_polygon(polygon)
face.add_loops([loop1, loop2, loop3], reverse=False)

brep = Brep.from_brepfaces([face])

# =============================================================================
# Visualization
# =============================================================================

viewer = Viewer()
viewer.scene.add(brep, linewidth=2, show_point=False)
viewer.show()
