import compas

from OCC.Core.Tesselator import ShapeTesselator

from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeEdge
)
from OCC.Core.BRepFill import BRepFill_Filling
from OCC.Core.TopoDS import TopoDS_Shell
from OCC.Core.gp import gp_Pnt

from OCC.Core.GeomAbs import GeomAbs_C0

from compas.datastructures import Mesh
from compas_view2.app import App

tubemesh = Mesh.from_obj(compas.get('tubemesh.obj'))

print(tubemesh.number_of_vertices())
print(tubemesh.number_of_faces())

# ==============================================================================
# To OCC
# ==============================================================================

shell = TopoDS_Shell()
builder = BRep_Builder()
builder.MakeShell(shell)

points = tubemesh.vertices_attributes('xyz')

for face in tubemesh.faces():
    brep = BRepFill_Filling()

    for u, v in tubemesh.face_halfedges(face):
        edge = BRepBuilderAPI_MakeEdge(gp_Pnt(* points[u]), gp_Pnt(* points[v])).Edge()
        brep.Add(edge, GeomAbs_C0, True)

    brep.Build()

    face = BRepBuilderAPI_MakeFace(brep.Face()).Face()
    builder.Add(shell, face)

# ==============================================================================
# Tesselation
# ==============================================================================

tess = ShapeTesselator(shell)
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

# ==============================================================================
# Viz
# ==============================================================================

print(mesh.number_of_vertices())
print(mesh.number_of_faces())

viewer = App()
viewer.add(mesh)
viewer.run()
