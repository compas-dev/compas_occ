# type: ignore
from compas.geometry import Frame
from compas.geometry import Box, Cylinder
from compas_view2.app import App

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

viewer = App(viewmode="ghosted", width=1600, height=900)
viewer.view.camera.rz = -30
viewer.view.camera.rx = -75
viewer.view.camera.distance = 7

viewer.add(result, linewidth=2)
viewer.run()
