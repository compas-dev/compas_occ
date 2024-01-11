from math import pi

from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeWire
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeShell
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeSolid

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder

from OCC.Core.BRep import BRep_Builder

from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.TopoDS import TopoDS_Shell
from OCC.Core.TopoDS import TopoDS_Solid
from OCC.Core.TopoDS import TopoDS_Wire
from OCC.Core.TopoDS import TopoDS_Face
from OCC.Core.TopoDS import TopoDS_Edge
from OCC.Core.TopoDS import TopoDS_Vertex

from OCC.Core.ShapeFix import ShapeFix_Wire

from OCC.Core.TopTools import TopTools_ListOfShape

from compas.geometry import Brep
from compas.geometry import Cylinder
from compas_occ import conversions

from compas_view2.app import App

cylinder = Brep.from_cylinder(Cylinder(1.0, 2.0))

builder = BRep_Builder()
shape = TopoDS_Shell()
builder.MakeShell(shape)

for face in cylinder.faces:
    if face.is_cylinder:
        wires = []
        for loop in face.loops:
            listofshape = TopTools_ListOfShape()
            for edge in loop.edges:
                if edge.is_line:
                    listofshape.Append(
                        BRepBuilderAPI_MakeEdge(
                            conversions.line_to_occ(edge.to_line()),
                            conversions.point_to_occ(edge.first_vertex.point),
                            conversions.point_to_occ(edge.last_vertex.point),
                        ).Edge()
                    )
                elif edge.is_circle:
                    listofshape.Append(
                        BRepBuilderAPI_MakeEdge(
                            conversions.circle_to_occ(edge.to_circle()),
                            edge.domain[0],
                            edge.domain[1],
                        ).Edge()
                    )
            wirebuilder = BRepBuilderAPI_MakeWire()
            wirebuilder.Add(listofshape)
            wire = wirebuilder.Wire()
            wires.append(wire)

        facebuilder = BRepBuilderAPI_MakeFace(
            conversions.cylinder_to_occ(face.to_cylinder()),
            *face.domain_u,
            *face.domain_v,
        )
        for wire in wires:
            facebuilder.Add(wire)
        builder.Add(shape, facebuilder.Face())

    if face.is_plane:
        plane = face.to_plane()
        surface = conversions.plane_to_occ(plane)
        # build the outer loop
        edges = []
        for edge in face.loops[0].edges:
            if edge.is_line:
                line = edge.to_line()
                edges.append(
                    BRepBuilderAPI_MakeEdge(
                        conversions.line_to_occ(line),
                        conversions.point_to_occ(line.start),
                        conversions.point_to_occ(line.end),
                    ).Edge()
                )
            elif edge.is_circle:
                circle = edge.to_circle()
                domain = edge.domain
                edges.append(
                    BRepBuilderAPI_MakeEdge(
                        conversions.circle_to_occ(circle),
                        domain[0],
                        domain[1],
                    ).Edge()
                )
        wire = BRepBuilderAPI_MakeWire()
        for edge in edges:
            wire.Add(edge)
        facebuilder = BRepBuilderAPI_MakeFace(
            surface,
            wire.Wire(),
        )
        # add the inner loops
        # add the face to the shell builder
        builder.Add(shape, facebuilder.Face())

brep = Brep.from_native(shape)
brep.make_solid()
brep.fix()
brep.sew()

viewer = App()
viewer.add(brep, linewidth=2)
viewer.run()
