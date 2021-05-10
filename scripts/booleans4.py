from compas.geometry import Polyline, Frame
from compas_occ.interop.shapes import Box, Sphere
from compas_occ.brep.booleans import boolean_union_shape_shape
from compas_occ.geometry.surfaces import BSplineSurface
from compas_occ.geometry.curves import BSplineCurve

from compas_view2.app import App
from compas_view2.objects import Object, BoxObject, SphereObject

from OCC.Core.BRep import BRep_Tool_Surface, BRep_Tool_Curve

Object.register(Box, BoxObject)
Object.register(Sphere, SphereObject)

box = Box(Frame.worldXY(), 1, 1, 1)
sphere = Sphere([0.5 * box.xsize, 0.5 * box.ysize, 0.5 * box.zsize], 0.5)
shape = boolean_union_shape_shape(box, sphere)
shape.convert()

viewer = App()

for face in shape.faces():
    srf = BRep_Tool_Surface(face)
    surface = BSplineSurface.from_occ(srf)
    viewer.add(surface.to_vizmesh(resolution=16), show_edges=True)

for edge in shape.edges():
    res = BRep_Tool_Curve(edge)
    if len(res) == 3:
        curve = BSplineCurve.from_occ(res[0])
        viewer.add(Polyline(curve.to_locus(resolution=16)), linecolor=(1, 0, 0), linewidth=5)

viewer.run()
