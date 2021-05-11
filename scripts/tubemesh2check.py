import compas
from compas.datastructures import Mesh
from compas_rhino.artists import MeshArtist

mesh = Mesh.from_obj(compas.get('tubemesh.obj'))

artist = MeshArtist(mesh)
artist.draw_faces(join_faces=True)
