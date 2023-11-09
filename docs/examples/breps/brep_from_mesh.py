# type: ignore

import compas
from compas.geometry import Vector, Translation, Scale
from compas.datastructures import Mesh
from compas.brep import Brep
from compas_view2.app import App


mesh: Mesh = Mesh.from_obj(compas.get("tubemesh.obj"))

# move the mesh closer to the origin
# place it on the XY plane
# and scale it down

centroid = mesh.centroid()
zmin = min(mesh.vertices_attribute("z"))
vector = Vector(*centroid)
vector.z = zmin
vector *= -1

T = Translation.from_vector(vector)
S = Scale.from_factors([0.3, 0.3, 0.3])

mesh.transform(S * T)

# convert to a brep

brep = Brep.from_mesh(mesh)

# visualize

viewer = App(viewmode="ghosted")
viewer.view.camera.position = [-9, -5, 1]
viewer.view.camera.look_at([3, 0, 1])

viewer.add(brep, linewidth=2)

viewer.run()
