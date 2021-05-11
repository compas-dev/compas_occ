import os
import compas
from compas.geometry import Point
from compas.datastructures import Mesh

from compas_occ.brep.datastructures import BRepShape
from compas_occ.geometry.curves import BSplineCurve
from compas_occ.geometry.surfaces.bspline import BSplineSurface

from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeFace,
)
from OCC.Core.TopoDS import TopoDS_Shell

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, '__tubemesh.stp')

mesh = Mesh.from_obj(compas.get('tubemesh.obj'))

shell = TopoDS_Shell()
builder = BRep_Builder()
builder.MakeShell(shell)

for face in mesh.faces():
    points = [Point(* point) for point in mesh.face_coordinates(face)]
    curve1 = BSplineCurve.from_points(points[:2])
    curve2 = BSplineCurve.from_points(points[3:] + points[2:3])
    surface = BSplineSurface.from_fill(curve1, curve2)
    face = BRepBuilderAPI_MakeFace(surface.occ_face).Face()
    builder.Add(shell, face)

shape = BRepShape(shell)
shape.to_step(FILE)
