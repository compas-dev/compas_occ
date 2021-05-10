from compas.geometry import Point, Line, Polyline, Frame
from compas_occ.interop.primitives import compas_point_from_occ_point
from compas_occ.interop.shapes import Box, Sphere
from compas_occ.brep.booleans import boolean_union_shape_shape
from compas_occ.geometry.curves import BSplineCurve

from compas_view2.app import App
from compas_view2.objects import Object, BoxObject, SphereObject

from OCC.Core.BRep import BRep_Tool_Pnt, BRep_Tool_Curve
from OCC.Extend.TopologyUtils import TopologyExplorer


Point.from_occ = classmethod(compas_point_from_occ_point)


Object.register(Box, BoxObject)
Object.register(Sphere, SphereObject)

box = Box(Frame.worldXY(), 1, 1, 1)
sphere = Sphere([0.5 * box.xsize, 0.5 * box.ysize, 0.5 * box.zsize], 0.5)
shape = boolean_union_shape_shape(box, sphere)

viewer = App()

shape_exp = TopologyExplorer(shape.occ_shape)

for vertex in shape_exp.vertices():
    pnt = BRep_Tool_Pnt(vertex)
    point = Point.from_occ(pnt)
    viewer.add(point, size=10, color=(1, 0, 0))

for face in shape_exp.faces():
    for edge in shape_exp.edges_from_face(face):
        res = BRep_Tool_Curve(edge)
        if len(res) == 3:
            crv, u, v = res

            start = Point.from_occ(crv.Value(u))
            end = Point.from_occ(crv.Value(v))

            viewer.add(Line(start, end))

            curve = BSplineCurve.from_occ(crv)
            viewer.add(Polyline(curve.to_locus(100)))

viewer.run()
