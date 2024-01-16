# type: ignore
from compas.geometry import Cylinder
from compas_view2.app import App

cylinder = Cylinder(1.0, 2.0).to_brep()

# =============================================================================
# Visualization
# =============================================================================

viewer = App()
viewer.view.camera.position = [2, -4, 1]
viewer.view.camera.look_at([0, 0, 0])

viewer.add(cylinder, opacity=0.9)
viewer.show()
