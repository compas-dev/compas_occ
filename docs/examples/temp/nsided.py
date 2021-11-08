import math
from compas.geometry import Polygon, Polyline, Rotation
from compas.geometry import normal_polygon

from compas_occ.geometry import OCCNurbsSurface
from compas_occ.geometry import OCCNurbsCurve
from compas_occ.brep import BRep

from compas_view2.app import App

from OCC.Core.BRepFill import BRepFill_Filling
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from OCC.Core.GeomAbs import GeomAbs_C0
from OCC.Core.gp import gp_Pnt
from OCC.Extend.TopologyUtils import TopologyExplorer

from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopoDS import topods_Face
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.TopLoc import TopLoc_Location

# ==============================================================================
# Input polygon
# ==============================================================================

R = Rotation.from_axis_and_angle([1, 1, 0], math.radians(30))

polygon = Polygon.from_sides_and_radius_xy(5, 2)
polygon.transform(R)

# ==============================================================================
# BRep Polygon
# ==============================================================================

points = [gp_Pnt(* point) for point in polygon]

poly = BRepBuilderAPI_MakePolygon()
for point in points:
    poly.Add(point)
poly.Build()
poly.Close()

# ==============================================================================
# BRep Filling
# ==============================================================================

edges = list(TopologyExplorer(poly.Wire()).edges())

nsided = BRepFill_Filling()
for edge in edges:
    nsided.Add(edge, GeomAbs_C0)
nsided.Add(gp_Pnt(* (polygon.centroid + normal_polygon(polygon))))
nsided.Build()

# ==============================================================================
# Surface from BRep Filling Face
# ==============================================================================

face = nsided.Face()
surface = OCCNurbsSurface.from_face(face)

# ==============================================================================
# BRep
# ==============================================================================

brep = BRep()
brep.shape = face

# mesh = brep.to_tesselation()

BRepMesh_IncrementalMesh(brep.shape, 0.1, False, 0.1, False)

bt = BRep_Tool()
ex = TopExp_Explorer(brep.shape, TopAbs_FACE)
while ex.More():
    face = topods_Face(ex.Current())
    location = TopLoc_Location()
    facing = (bt.Triangulation(face, location))
    tab = facing.Nodes()
    tri = facing.Triangles()
    for i in range(1, facing.NbTriangles() + 1):
        trian = tri.Value(i)
        index1, index2, index3 = trian.Get()
        # for j in range(1, 4):
        #     if j == 1:
        #         m = index1
        #         n = index2
        #     elif j == 2:
        #         n = index3
        #     elif j == 3:
        #         m = index2
        #     me = BRepBuilderAPI_MakeEdge(tab.Value(m), tab.Value(n))
        #     if me.IsDone():
        #         builder.Add(comp, me.Edge())
    ex.Next()

# ==============================================================================
# Viz
# ==============================================================================

viewer = App()

# viewer.add(surface.to_mesh())
viewer.add(mesh)

for edge in edges:
    curve = OCCNurbsCurve.from_edge(edge)
    viewer.add(Polyline(curve.locus(resolution=16)), linecolor=(1, 0, 0), linewidth=5)

viewer.run()
