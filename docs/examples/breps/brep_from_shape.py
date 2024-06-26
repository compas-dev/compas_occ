from compas.geometry import Cylinder
from compas_viewer import Viewer

cylinder = Cylinder(1.0, 2.0).to_brep()

# =============================================================================
# Visualization
# =============================================================================

viewer = Viewer()

viewer.renderer.camera.target = [0, 0, 0]
viewer.renderer.camera.position = [2, -4, 1]

viewer.scene.add(cylinder, opacity=0.9, show_points=False)

viewer.show()
