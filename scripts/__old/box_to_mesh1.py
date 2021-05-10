from OCC.Core.Tesselator import ShapeTesselator
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox

from compas.datastructures import Mesh
from compas_view2.app import App

box = BRepPrimAPI_MakeBox(1, 1, 1).Shape()

tess = ShapeTesselator(box)
tess.Compute(compute_edges=True)

vertices = []
triangles = []
edges = []

for i in range(tess.ObjGetVertexCount()):
    xyz = tess.GetVertex(i)
    vertices.append(xyz)

for i in range(tess.ObjGetTriangleCount()):
    a, b, c = tess.GetTriangleIndex(i)
    triangles.append([a, b, c])

for i in range(tess.ObjGetEdgeCount()):
    edge = []
    for j in range(tess.ObjEdgeGetVertexCount(i)):
        edge.append(j)
    edges.append(edge)

print(vertices)
print(triangles)
print(edges)

mesh = Mesh.from_vertices_and_faces(vertices, triangles)

view = App()
view.add(mesh)
view.run()
