from compas.geometry import Point
from compas.geometry import Circle
from compas.geometry import Plane
from compas.geometry import Vector
from compas_occ.brep.brepedge import BRepEdge
from compas_occ.geometry import OCCNurbsSurface
from compas_occ.geometry import OCCNurbsCurve
from compas_occ.geometry import OCCCurve
from compas_occ.brep import BRepLoop
from compas_occ.brep import BRepFace
from compas_occ.brep import BRep
from compas_view2.app import App

from OCC.Core.GeomProjLib import geomprojlib_Project
from OCC.Core.GeomProjLib import geomprojlib_Curve2d

points = [
    [Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0), Point(3, 0, 0)],
    [Point(0, 1, 0), Point(1, 1, 2), Point(2, 1, 2), Point(3, 1, 0)],
    [Point(0, 2, 0), Point(1, 2, 2), Point(2, 2, 2), Point(3, 2, 0)],
    [Point(0, 3, 0), Point(1, 3, 0), Point(2, 3, 0), Point(3, 3, 0)],
]

surface = OCCNurbsSurface.from_points(points=points)

curve = OCCNurbsCurve.from_circle(
    Circle(Plane(Point(1.5, 1.5, 1.5), Vector(0, 0, 1)), 0.5)
)

result = geomprojlib_Project(curve.occ_curve, surface.occ_surface)
projection = OCCCurve.from_occ(result)

result = geomprojlib_Curve2d(projection.occ_curve, surface.occ_surface)
curve2d = OCCCurve.from_occ(result)

edge = BRepEdge.from_curve(curve2d, surface)
loop = BRepLoop.from_edges([edge])
face = BRepFace.from_surface(surface, loop=loop, inside=False)
brep = BRep.from_faces([face])

print(brep.shape)

mesh = brep.to_tesselation()
print(mesh)

for edge in brep.edges:
    print(edge)

viewer = App()

for mesh in brep.to_meshes():
    viewer.add(mesh)
# viewer.add(surface.to_mesh())
viewer.add(curve.to_polyline())
viewer.add(projection.to_polyline(), color=(1.0, 0, 0), linewidth=5)

viewer.show()
