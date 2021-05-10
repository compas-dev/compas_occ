from compas.geometry import Frame, Translation
from compas_occ.brep.primitives import Box, Sphere
from compas_occ.brep.booleans import boolean_union_shape_shape

from compas_view2.app import App
from compas_view2.objects import Object, BoxObject, SphereObject

Object.register(Box, BoxObject)
Object.register(Sphere, SphereObject)

box = Box(Frame.worldXY(), 1, 1, 1)
sphere = Sphere([0.5 * box.xsize, 0.5 * box.ysize, 0.5 * box.zsize], 0.5)

shape = boolean_union_shape_shape(box, sphere)

viewer = App()
viewer.add(box, show_edges=True)
viewer.add(sphere, show_edges=True)
viewer.add(shape.to_tesselation().transformed(Translation.from_vector([2, 0, 0])), show_edges=True)
viewer.run()

