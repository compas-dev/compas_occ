from compas_viewer import Viewer

from compas.geometry import Box
from compas.geometry import Cylinder
from compas.geometry import Frame
from compas.tolerance import TOL

# from compas_occ.brep import OCCBrep

TOL.lineardeflection = 0.1

R = 1.4
YZ = Frame.worldYZ()
ZX = Frame.worldZX()
XY = Frame.worldXY()

box = Box(2 * R).to_brep()
cx = Cylinder(0.7 * R, 4 * R, frame=YZ).to_brep()
cy = Cylinder(0.7 * R, 4 * R, frame=ZX).to_brep()
cz = Cylinder(0.7 * R, 4 * R, frame=XY).to_brep()

# result = OCCBrep.from_boolean_difference(box, [cx, cy, cz])
result = box - (cx + cy + cz)

result.to_step("/Users/vanmelet/Desktop/booleans.step")

# ==============================================================================
# Visualisation
# ==============================================================================

viewer = Viewer()

viewer.renderer.camera.target = [0, 0, 0]
viewer.renderer.camera.position = [4, -6, 2]

viewer.scene.add(result, linewidth=2, show_points=False)

viewer.show()
