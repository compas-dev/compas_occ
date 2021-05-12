import math
from compas.geometry import Point, Polygon, Polyline, Rotation

from compas_occ.geometry.surfaces import BSplineSurface
from compas_occ.geometry.curves import BSplineCurve

from compas_view2.app import App

from OCC.Core.BRepFill import BRepFill_Filling
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from OCC.Core.GeomAbs import GeomAbs_C0
from OCC.Core.gp import gp_Pnt
from OCC.Extend.TopologyUtils import TopologyExplorer


polygon = Polygon.from_sides_and_radius_xy(5, 2).transformed(Rotation.from_axis_and_angle([1, 1, 0], math.radians(30)))
points = [gp_Pnt(* point) for point in polygon]

poly = BRepBuilderAPI_MakePolygon()
for point in points:
    poly.Add(point)
poly.Build()
poly.Close()

edges = TopologyExplorer(poly.Wire()).edges()

nsided = BRepFill_Filling()
for edge in edges:
    nsided.Add(edge, GeomAbs_C0)
nsided.Add(gp_Pnt(* (polygon.centroid + Point(0, 0, 0.2))))
nsided.Build()

face = nsided.Face()

surface = BSplineSurface.from_face(face)

viewer = App()

viewer.add(surface.to_vizmesh(resolution=100))
viewer.add(polygon, linewidth=5, linecolor=(1, 0, 0))
for edge in edges:
    curve = BSplineCurve.from_edge(edge)
    if curve:
        viewer.add(Polyline(curve.to_locus(resolution=16)), linecolor=(1, 0, 0), linewidth=5)

viewer.run()


# def build_plate(polygon, points):
#     '''
#     build a surface from a constraining polygon(s) and point(s)
#     @param polygon:     list of polygons ( TopoDS_Shape)
#     @param points:      list of points ( gp_Pnt )
#     '''
#     # plate surface
#     bpSrf = GeomPlate_BuildPlateSurface(3, 15, 2)

#     # add curve constraints
#     for poly in polygon:
#         for edg in WireExplorer(poly).ordered_edges():
#             c = BRepAdaptor_HCurve()
#             c.ChangeCurve().Initialize(edg)
#             constraint = BRepFill_CurveConstraint(c, 0)
#             bpSrf.Add(constraint)

#     # add point constraint
#     for pt in points:
#         bpSrf.Add(GeomPlate_PointConstraint(pt, 0))
#         bpSrf.Perform()

#     maxSeg, maxDeg, critOrder = 9, 8, 0
#     tol = 1e-4
#     dmax = max([tol, 10 * bpSrf.G0Error()])

#     srf = bpSrf.Surface()
#     plate = GeomPlate_MakeApprox(srf, tol, maxSeg, maxDeg, dmax, critOrder)
#     uMin, uMax, vMin, vMax = srf.Bounds()

#     return make_face(plate.Surface(), uMin, uMax, vMin, vMax, 1e-4)


# def build_geom_plate(edges):
#     bpSrf = GeomPlate_BuildPlateSurface(3, 9, 12)

#     # add curve constraints
#     for edg in edges:
#         c = BRepAdaptor_HCurve()
#         print('edge:', edg)
#         c.ChangeCurve().Initialize(edg)
#         constraint = BRepFill_CurveConstraint(c, 0)
#         bpSrf.Add(constraint)

#     # add point constraint
#     try:
#         bpSrf.Perform()
#     except RuntimeError:
#         print('failed to build the geom plate surface ')

#     srf = bpSrf.Surface()
#     plate = GeomPlate_MakeApprox(srf, 0.01, 10, 5, 0.01, 0, GeomAbs_C0)

#     uMin, uMax, vMin, vMax = srf.Bounds()
#     face = make_face(plate.Surface(), uMin, uMax, vMin, vMax, 1e-6)
#     return
