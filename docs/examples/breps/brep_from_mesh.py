# type: ignore
import compas
from compas.datastructures import Mesh
from compas.geometry import Brep
from compas_view2.app import App

# Construct a mesh from an OBJ file
# and convert to a brep

mesh: Mesh = Mesh.from_obj(compas.get("tubemesh.obj"))
brep = Brep.from_mesh(mesh)

# =============================================================================
# Visualization
# =============================================================================

viewer = App(width=1600, height=900)
viewer.view.camera.position = [1, -6, 2]
viewer.view.camera.look_at([1, 1, 1])

viewer.add(brep, linewidth=2)
viewer.run()
