import compas

from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeVertex,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeWire
)
from OCC.Core.TopoDS import TopoDS_Shell
from OCC.Core.gp import gp_Pnt

from OCC.Core.BRep import BRep_Tool
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopoDS import topods_Vertex, topods_Wire
from OCC.Core.TopAbs import TopAbs_WIRE, TopAbs_VERTEX

from compas.datastructures import Mesh
from compas_view2.app import App

tubemesh = Mesh.from_obj(compas.get('tubemesh.obj'))
tubemesh.quads_to_triangles()

print(tubemesh.number_of_vertices())
print(tubemesh.number_of_faces())

# ==============================================================================
# To OCC
# ==============================================================================

shell = TopoDS_Shell()
builder = BRep_Builder()
builder.MakeShell(shell)

vertexdict = {vertex: BRepBuilderAPI_MakeVertex(gp_Pnt(* tubemesh.vertex_attributes(vertex, 'xyz'))) for vertex in tubemesh.vertices()}

for face in tubemesh.faces():
    wire = BRepBuilderAPI_MakeWire()
    for u, v in tubemesh.face_halfedges(face):
        edge = BRepBuilderAPI_MakeEdge(vertexdict[u].Vertex(), vertexdict[v].Vertex())
        wire.Add(edge.Edge())
    face = BRepBuilderAPI_MakeFace(wire.Wire()).Face()
    builder.Add(shell, face)

# ==============================================================================
# Explore
# ==============================================================================

polygons = []

tool = BRep_Tool()
wires = TopExp_Explorer(shell, TopAbs_WIRE)

while wires.More():
    wire = topods_Wire(wires.Current())
    vertices = TopExp_Explorer(wire, TopAbs_VERTEX)
    points = []

    while vertices.More():
        vertex = topods_Vertex(vertices.Current())
        point = tool.Pnt(vertex)
        x = point.X()
        y = point.Y()
        z = point.Z()
        points.append([x, y, z])
        vertices.Next()

    polygons.append(points)
    wires.Next()

# ==============================================================================
# Viz
# ==============================================================================

mesh = Mesh.from_polygons(polygons)

print(mesh.number_of_vertices())
print(mesh.number_of_faces())

viewer = App()
viewer.add(mesh)
viewer.run()
