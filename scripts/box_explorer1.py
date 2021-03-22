from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopoDS import topods_Face, topods_Vertex
from OCC.Core.TopAbs import TopAbs_FACE, TopAbs_VERTEX

from compas.datastructures import Mesh
from compas_view2.app import App

box = BRepPrimAPI_MakeBox(1, 1, 1).Shape()

print(box.NbChildren())
print(box.ShapeType())

tool = BRep_Tool()

polygons = []

faces = TopExp_Explorer(box, TopAbs_FACE)

while faces.More():
    face = topods_Face(faces.Current())
    vertices = TopExp_Explorer(face, TopAbs_VERTEX)
    points = []

    while vertices.More():
        vertex = topods_Vertex(vertices.Current())
        point = tool.Pnt(vertex)
        x = point.X()
        y = point.Y()
        z = point.Z()
        points.append([x, y, z])
        vertices.Next()

    polygons.append(points[:4])
    polygons.append(points[4:])
    faces.Next()

mesh = Mesh.from_polygons(polygons)

viewer = App()
viewer.add(mesh)
viewer.run()
