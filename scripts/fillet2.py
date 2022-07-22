import os

from compas.geometry import Frame
from compas.geometry import Box, Cylinder
from compas_occ.brep import BRep

from compas_view2.app import App
from compas_view2.objects import Collection

from OCC.Core.BRepFilletAPI import BRepFilletAPI_MakeChamfer

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, "fillet.stp")

box = Box(Frame.worldXY(), 1.8, 1.8, 2)
box.frame.point.z += 0.2
box = BRep.from_box(box)

fillet = BRepFilletAPI_MakeChamfer(box.occ_shape)
for edge in box.edges:
    fillet.Add(0.1, edge.occ_edge)
fillet.Build()

void = BRep()
void.occ_shape = fillet.Shape()

shape = BRep.from_box(Box(Frame.worldXY(), 2, 2, 2))
shape = shape - void

cylinder = Cylinder((([1, 1, 0], [0, 0, 1]), 0.4), 3)
cylinder = BRep.from_cylinder(cylinder)

shape = shape + cylinder

viewer = App()

viewmesh = shape.to_viewmesh()
viewer.add(viewmesh[0], show_edges=False)
viewer.add(Collection(viewmesh[1]), linewidth=2)

viewer.run()
