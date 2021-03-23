import compas
from OCC.Extend.ShapeFactory import make_n_sided
from afem.topology.create import EdgeByPoints, ShellBySewing, Face
from compas.datastructures import Mesh

tubemesh = Mesh.from_obj(compas.get('tubemesh.obj'))

nr_verts_compas = tubemesh.number_of_vertices()
nr_faces_compas = tubemesh.number_of_faces()

points = tubemesh.vertices_attributes('xyz')

_shells = []
for face in tubemesh.faces():

    _edges = []
    for u, v in tubemesh.face_halfedges(face):
        pnt_u, pnt_v = points[u], points[v]

        edge = EdgeByPoints(pnt_u, pnt_v)
        _edges.append(edge)

    # meh, proper AFEM method is required...
    _face = make_n_sided([e._e.object for e in _edges])
    face = Face(_face)
    _shells.append(face)

shell = ShellBySewing(_shells)

assert shell.shell.num_faces == nr_faces_compas
assert shell.shell.num_vertices == nr_verts_compas
