# type: ignore
from math import radians
from compas.geometry import Box
from compas.geometry import Plane
from compas.geometry import Rotation
from compas_view2.app import App

box = Box(1).to_brep()

R = Rotation.from_axis_and_angle([0, 1, 0], radians(30))
plane = Plane.worldXY()
plane.transform(R)

trimmed = box.trimmed(plane)

# =============================================================================
# Visualization
# =============================================================================

viewer = App()
viewer.view.camera.position = [2, -4, 1]
viewer.view.camera.look_at([0, 0, 0])

viewer.add(plane, opacity=0.5)
viewer.add(trimmed, linewidth=2)
viewer.add(box, linewidth=1, show_faces=False)
viewer.show()
