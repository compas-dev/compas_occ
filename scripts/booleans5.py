from compas.geometry import Polyline, Frame

from compas_occ.conversions.shapes import Box, Sphere
from compas_occ.brep.booleans import boolean_intersection_shape_shape
from compas_occ.geometry.surfaces import BSplineSurface
from compas_occ.geometry.curves import BSplineCurve

from compas_view2.app import App
from compas_view2.objects import Object, BoxObject, SphereObject

Object.register(Box, BoxObject)
Object.register(Sphere, SphereObject)

box = Box(Frame.worldXY(), 1, 1, 1)
sphere = Sphere([0.5 * box.xsize, 0.5 * box.ysize, 0.5 * box.zsize], 0.5)

shape = boolean_intersection_shape_shape(box, sphere, convert=True)

viewer = App()

for face in shape.faces():
    surface = BSplineSurface.from_face(face)
    viewer.add(surface.to_vizmesh(resolution=16))

for edge in shape.edges():
    curve = BSplineCurve.from_edge(edge)
    if curve:
        viewer.add(Polyline(curve.to_locus(resolution=16)), linecolor=(1, 0, 0), linewidth=5)

viewer.run()
