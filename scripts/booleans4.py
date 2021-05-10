from compas.geometry import Polyline, Frame
from compas_occ.brep.primitives import Box, Sphere
from compas_occ.brep.booleans import boolean_union_shape_shape
from compas_occ.geometry.surfaces import BSplineSurface
from compas_occ.geometry.curves import BSplineCurve

from compas_view2.app import App
from compas_view2.objects import Object, BoxObject, SphereObject

from OCC.Core.BRep import BRep_Tool_Surface, BRep_Tool_Curve
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert
from OCC.Extend.TopologyUtils import TopologyExplorer

Object.register(Box, BoxObject)
Object.register(Sphere, SphereObject)

box = Box(Frame.worldXY(), 1, 1, 1)
sphere = Sphere([0.5 * box.xsize, 0.5 * box.ysize, 0.5 * box.zsize], 0.5)
shape = boolean_union_shape_shape(box, sphere)

viewer = App()

converter = BRepBuilderAPI_NurbsConvert(shape.occ_shape, True)
shape_exp = TopologyExplorer(converter.Shape())

for face in shape_exp.faces():
    srf = BRep_Tool_Surface(face)
    surface = BSplineSurface.from_occ(srf)
    viewer.add(surface.to_vizmesh(resolution=16), show_edges=True)

for edge in shape_exp.edges():
    res = BRep_Tool_Curve(edge)
    if len(res) == 3:
        crv, u, v = res
        curve = BSplineCurve.from_occ(crv)
        viewer.add(Polyline(curve.to_locus(resolution=16)), linecolor=(1, 0, 0), linewidth=5)

viewer.run()
