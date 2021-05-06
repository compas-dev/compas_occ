from compas.datastructures import Mesh
from compas_view2.app import App

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere
from OCC.Core.BRep import BRep_Tool
from OCC.Core.TopoDS import topods_Vertex, topods_Wire
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_WIRE, TopAbs_VERTEX

tool = BRep_Tool()

sphere = BRepPrimAPI_MakeSphere(1).Shape()

wires = TopExp_Explorer(sphere, TopAbs_WIRE)
polygons = []

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

mesh = Mesh.from_polygons(polygons)

viewer = App()
viewer.add(mesh)
viewer.run()
