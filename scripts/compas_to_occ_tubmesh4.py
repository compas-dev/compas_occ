import compas

from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakePolygon,
    BRepBuilderAPI_MakeVertex,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeWire
)
from OCC.Core.BRepFill import BRepFill_Filling
from OCC.Core.TopoDS import TopoDS_Shell, TopoDS_Vertex, TopoDS_Edge, topods_Wire, topods_Vertex
from OCC.Core.gp import gp_Pnt

from OCC.Core.BRep import BRep_Tool
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_WIRE, TopAbs_VERTEX
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
