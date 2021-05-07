from compas.geometry import Frame
from compas.datastructures import Mesh

from compas_view2.app import App

from OCC.Core.BRep import BRep_Tool
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopoDS import topods_Vertex, topods_Wire
from OCC.Core.TopAbs import TopAbs_WIRE, TopAbs_VERTEX

from compas_occ.brep.shapes.monkey import Box

box = Box(Frame.worldXY(), 1, 1, 1)
shell = box.to_occ()

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
print(mesh.number_of_edges())
print(mesh.number_of_faces())

viewer = App()
viewer.add(mesh)
viewer.run()
