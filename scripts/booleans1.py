import os

from compas.geometry import Frame
from compas_occ.interop.shapes import Box, Sphere
from compas_occ.brep.booleans import boolean_union_shape_shape

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, '__fuse.stp')

box = Box(Frame.worldXY(), 1, 1, 1)
sphere = Sphere([0.5 * box.xsize, 0.5 * box.ysize, 0.5 * box.zsize], 0.5)

shape = boolean_union_shape_shape(box, sphere)

shape.to_step(FILE)
