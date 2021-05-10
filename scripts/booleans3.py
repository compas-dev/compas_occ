from compas.geometry import Point, Line, Polyline, Frame
from compas_occ.brep.primitives import Box, Sphere
from compas_occ.brep.booleans import boolean_union_shape_shape
from compas_occ.geometry.surfaces.bspline import BSplineSurface
from compas_occ.geometry.curves.bspline import BSplineCurve

from compas_view2.app import App
from compas_view2.objects import Object, BoxObject, SphereObject

from OCC.Core.BRep import BRep_Tool_Surface, BRep_Tool_Pnt, BRep_Tool_Curve, BRep_Tool_CurveOnSurface
from OCC.Extend.TopologyUtils import TopologyExplorer

Object.register(Box, BoxObject)
Object.register(Sphere, SphereObject)

box = Box(Frame.worldXY(), 1, 1, 1)
sphere = Sphere([0.5 * box.xsize, 0.5 * box.ysize, 0.5 * box.zsize], 0.5)
shape = boolean_union_shape_shape(box, sphere)

viewer = App()

shape_exp = TopologyExplorer(shape.occ_shape)

for vertex in shape_exp.vertices():
    pnt = BRep_Tool_Pnt(vertex)
    point = Point(pnt.X(), pnt.Y(), pnt.Z())
    viewer.add(point, size=10, color=(1, 0, 0))

for face in shape_exp.faces():
    srf = BRep_Tool_Surface(face)
    # surface = BSplineSurface.from_occ(srf)
    # mesh = surface.to_vizmesh(resolution=16)
    # viewer.add(mesh, show_edges=True)
    for edge in shape_exp.edges_from_face(face):
        res = BRep_Tool_Curve(edge)
        if len(res) == 3:
            crv, u, v = res

            pnt = crv.Value(u)
            start = Point(pnt.X(), pnt.Y(), pnt.Z())

            pnt = crv.Value(v)
            end = Point(pnt.X(), pnt.Y(), pnt.Z())

            viewer.add(Line(start, end))

            curve = BSplineCurve.from_occ(crv)
            viewer.add(Polyline(curve.to_locus(100)))

viewer.run()

