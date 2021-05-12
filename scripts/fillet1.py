import os

from compas.geometry import Frame
from compas_occ.interop.shapes import Box
from compas_occ.brep.datastructures import BRepShape

from OCC.Core.BRepFilletAPI import BRepFilletAPI_MakeFillet

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, '__fillet.stp')

box = BRepShape(Box(Frame.worldXY(), 1, 1, 1).to_occ_shape())
fillet = BRepFilletAPI_MakeFillet(box.occ_shape)

for edge in box.edges():
    fillet.Add(0.1, edge)

shape = BRepShape(fillet.Shape())
shape.to_step(FILE)
