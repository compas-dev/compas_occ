from compas.geometry import Box
from compas.geometry import Cylinder
from compas.geometry import Frame
from compas.tolerance import TOL
from compas_viewer import Viewer

TOL.lineardeflection = 0.1

R = 1.4
YZ = Frame.worldYZ()
ZX = Frame.worldZX()
XY = Frame.worldXY()

box = Box(2 * R).to_brep()
cx = Cylinder(0.7 * R, 4 * R, frame=YZ).to_brep()
cy = Cylinder(0.7 * R, 4 * R, frame=ZX).to_brep()
cz = Cylinder(0.7 * R, 4 * R, frame=XY).to_brep()

result = box - (cx + cy + cz)

# ==============================================================================
# Visualisation
# ==============================================================================

viewer = Viewer()

# viewer.view.camera.rz = -30
# viewer.view.camera.rx = -75
# viewer.view.camera.distance = 7

viewer.scene.add(result, linewidth=2, show_points=False)

viewer.show()
