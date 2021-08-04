import compas
from compas.geometry import Vector, Translation, Scale
from compas.datastructures import Mesh
from compas_occ.brep import BRep
from compas_view2.app import App

mesh = Mesh.from_obj(compas.get('tubemesh.obj'))

centroid = mesh.centroid()
zmin = min(mesh.vertices_attribute('z'))
vector = Vector(*centroid)
vector.z = zmin
vector *= -1

T = Translation.from_vector(vector)
S = Scale.from_factors([0.3, 0.3, 0.3])

mesh.transform(S * T)

brep = BRep.from_mesh(mesh)
tess = brep.to_tesselation()

viewer = App()
viewer.add(tess)
viewer.run()
