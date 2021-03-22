from compas.geometry import Frame, Box

from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCC.Core.TopoDS import TopoDS_Shell
from OCC.Core.gp import gp_Pnt

from OCC.Core.BRep import BRep_Tool
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopoDS import topods_Vertex, topods_Wire
from OCC.Core.TopAbs import TopAbs_WIRE, TopAbs_VERTEX

from compas.datastructures import Mesh
from compas_view2.app import App

box = Box(Frame.worldXY(), 1, 1, 1)

# ==============================================================================
# To OCC
# ==============================================================================

shell = TopoDS_Shell()

builder = BRep_Builder()
builder.MakeShell(shell)

vertices = [gp_Pnt(*xyz) for xyz in box.vertices]

for face in box.faces:
    polygon = BRepBuilderAPI_MakePolygon()
    for vertex in face:
        polygon.Add(vertices[vertex])

    wire = polygon.Wire()
    shape = BRepBuilderAPI_MakeFace(wire).Shape()
    builder.Add(shell, shape)

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

viewer = App()
viewer.add(mesh)
viewer.run()
