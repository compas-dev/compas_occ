import os
import compas
from compas.datastructures import Mesh

from compas_occ.brep.datastructures import BRepShape

from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakePolygon,
    BRepBuilderAPI_MakeFace,
)
from OCC.Core.TopoDS import TopoDS_Shell
from OCC.Core.gp import gp_Pnt

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, '__tubemesh.stp')

mesh = Mesh.from_obj(compas.get('tubemesh.obj'))
mesh.quads_to_triangles()

shell = TopoDS_Shell()
builder = BRep_Builder()
builder.MakeShell(shell)

for face in mesh.faces():
    polygon = BRepBuilderAPI_MakePolygon()
    for point in mesh.face_coordinates(face):
        polygon.Add(gp_Pnt(* point))
    wire = polygon.Wire()
    face = BRepBuilderAPI_MakeFace(wire).Face()
    builder.Add(shell, face)

shape = BRepShape(shell)
shape.to_step(FILE)
