from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeWire
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeShell
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeSolid

from OCC.Core.BRep import BRep_Builder

from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.TopoDS import TopoDS_Shell
from OCC.Core.TopoDS import TopoDS_Solid
from OCC.Core.TopoDS import TopoDS_Wire
from OCC.Core.TopoDS import TopoDS_Face
from OCC.Core.TopoDS import TopoDS_Edge
from OCC.Core.TopoDS import TopoDS_Vertex

from compas.geometry import Brep
from compas.geometry import Box
from compas_occ import conversions

from compas_view2.app import App

box = Brep.from_box(Box(1, 1, 1))

builder = BRep_Builder()
shape = TopoDS_Shell()
builder.MakeShell(shape)

# make a shape from faces
# make a face from a surface with a domain, and by adding wires one by one
# make a wire from a list of edges
# make and edge from a curve, two points and a domain

for face in box.faces:
    # get the surface geometry
    plane = face.to_plane()
    # build the outer loop
    edges = []
    for edge in face.loops[0].edges:
        line = edge.to_line()
        edges.append(
            BRepBuilderAPI_MakeEdge(
                conversions.line_to_occ(line),
                conversions.point_to_occ(line.start),
                conversions.point_to_occ(line.end),
            ).Edge()
        )
    wire = BRepBuilderAPI_MakeWire()
    for edge in edges:
        wire.Add(edge)
    # build the face from the surface geometry and the outer loop
    facebuilder = BRepBuilderAPI_MakeFace(
        conversions.plane_to_occ(plane),
        wire.Wire(),
    )
    # add the inner loops
    # add the face to the shell builder
    builder.Add(shape, facebuilder.Face())

brep = Brep.from_native(shape)
brep.sew()
brep.fix()

viewer = App()
viewer.add(brep, lineswidth=2)
viewer.run()
