# type: ignore

import compas
from compas.datastructures import Mesh
from compas.geometry import Brep
from compas_view2.app import App


mesh: Mesh = Mesh.from_obj(compas.get("tubemesh.obj"))

# convert to a brep

brep = Brep.from_mesh(mesh)

# visualize

viewer = App(width=1600, height=900)
viewer.view.camera.position = [1, -6, 2]
viewer.view.camera.look_at([1, 1, 1])

viewer.add(brep, linewidth=2)

viewer.run()
