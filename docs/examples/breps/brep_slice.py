from math import radians

from compas.geometry import Box
from compas.geometry import Plane
from compas.geometry import Rotation
from compas_viewer import Viewer

box = Box(1).to_brep()

plane = Plane.worldXY()
R = Rotation.from_axis_and_angle([0, 1, 0], radians(30))
plane.transform(R)

slice = box.slice(plane)

# =============================================================================
# Visualization
# =============================================================================

viewer = Viewer()

viewer.renderer.camera.target = [0, 0, 0]
viewer.renderer.camera.position = [2, -4, 1]

viewer.scene.add(box, opacity=0.5, show_points=False)
viewer.scene.add(slice, linewidth=2)

viewer.show()
