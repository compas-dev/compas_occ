import os

from compas.geometry import Frame
from compas_occ.brep.primitives import Box, Sphere
from compas_occ.brep.booleans import boolean_union_shape_shape

# from OCC.Extend.TopologyUtils import TopologyExplorer

from compas_view2.app import App
from compas_view2.objects import Object, BoxObject, SphereObject

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, '__fuse.stp')

Object.register(Box, BoxObject)
Object.register(Sphere, SphereObject)

box = Box(Frame.worldXY(), 1, 1, 1)
sphere = Sphere([0.5 * box.xsize, 0.5 * box.ysize, 0.5 * box.zsize], 0.5)

shape = boolean_union_shape_shape(box, sphere)

shape.to_step(FILE)

# exp = TopologyExplorer(shape)
# print(exp.number_of_vertices())
# print(exp.number_of_edges())
# print(exp.number_of_faces())
# print(exp.number_of_wires())
# print(exp.number_of_shells())
# print(exp.number_of_solids())
# print(exp.number_of_compounds())

# step_writer = STEPControl_Writer()
# Interface_Static_SetCVal("write.step.schema", "AP203")

# step_writer.Transfer(shape, STEPControl_AsIs)
# status = step_writer.Write(FILE)

# if status != IFSelect_RetDone:
# 	raise AssertionError("load failed")

# viewer = App()
# viewer.add(box, show_edges=True)
# viewer.add(sphere, show_edges=True)
# viewer.run()

