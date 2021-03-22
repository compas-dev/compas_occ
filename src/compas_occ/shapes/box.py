from compas.geometry import Box

from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakePolygon,
    BRepBuilderAPI_MakeFace
)
from OCC.Core.TopoDS import TopoDS_Shell
from OCC.Core.gp import gp_Pnt


class Box(Box):

    def to_occ(self):
        """Convert a COMPAS box to an OCC BRep."""
        shell = TopoDS_Shell()
        builder = BRep_Builder()
        builder.MakeShell(shell)
        vertices = [gp_Pnt(*xyz) for xyz in self.vertices]
        for face in self.faces:
            polygon = BRepBuilderAPI_MakePolygon()
            for vertex in face:
                polygon.Add(vertices[vertex])
            wire = polygon.Wire()
            shape = BRepBuilderAPI_MakeFace(wire).Shape()
            builder.Add(shell, shape)
        return shell
