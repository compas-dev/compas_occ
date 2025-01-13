from compas_viewer import Viewer

from compas.colors import Color
from compas.geometry import Cylinder
from compas.geometry import Torus

cylinder = Cylinder(radius=1.0, height=2.0).to_brep()
torus = Torus(radius_axis=1.5, radius_pipe=0.3).to_brep()

# =============================================================================
# Visualization
# =============================================================================

viewer = Viewer()

viewer.renderer.camera.target = [0, 0, 0]
viewer.renderer.camera.position = [2, -4, 1]

viewer.scene.add(cylinder, opacity=0.9, show_points=False, linewidth=2)
viewer.scene.add(torus, opacity=0.9, show_points=False, linewidth=2, facecolor=Color.green())

viewer.show()
