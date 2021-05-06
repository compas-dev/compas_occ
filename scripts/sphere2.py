from compas.datastructures import Mesh
from compas_view2.app import App

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere
from OCC.Core.Tesselator import ShapeTesselator

sphere = BRepPrimAPI_MakeSphere(1).Shape()

tess = ShapeTesselator(sphere)
tess.Compute()

vertices = []
triangles = []

for i in range(tess.ObjGetVertexCount()):
    xyz = tess.GetVertex(i)
    vertices.append(xyz)

for i in range(tess.ObjGetTriangleCount()):
    a, b, c = tess.GetTriangleIndex(i)
    triangles.append([a, b, c])

mesh = Mesh.from_vertices_and_faces(vertices, triangles)

view = App()
view.add(mesh)
view.run()
