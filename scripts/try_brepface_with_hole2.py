from compas.geometry import Point, Plane, Circle
from compas.utilities import meshgrid, flatten
from compas_occ.geometry import OCCNurbsCurve, OCCNurbsSurface
from compas_occ.brep import BRepEdge, BRepLoop, BRepFace
from compas_occ.brep import BRep
from compas_view2.app import App

# from OCC.Core.ShapeAnalysis import ShapeAnalysis_Shell

surface = OCCNurbsSurface.from_points(
    [[Point(-5, -5, 0), Point(+5, -5, 0)], [Point(-5, +5, 0), Point(+5, +5, 0)]]
    # [[Point(-5, -5, 0), Point(-5, +5, 0)], [Point(+5, -5, 0), Point(+5, +5, 0)]]
)

circle1 = Circle(Plane([2, 2, 0], [0, 0, 1]), 1.0)
circle2 = Circle(Plane([-2, -2, 0], [0, 0, 1]), 2.0)
circle3 = Circle(Plane([2, -2, 0], [0, 0, 1]), 0.5)

curve1 = OCCNurbsCurve.from_circle(circle1).embedded(surface)
curve2 = OCCNurbsCurve.from_circle(circle2).embedded(surface)
curve3 = OCCNurbsCurve.from_circle(circle3).embedded(surface)

edge1 = BRepEdge.from_curve(curve1, surface)
edge2 = BRepEdge.from_curve(curve2, surface)
edge3 = BRepEdge.from_curve(curve3, surface)

loop1 = BRepLoop.from_edges([edge1])
loop2 = BRepLoop.from_edges([edge2])
loop3 = BRepLoop.from_edges([edge3])

face = BRepFace.from_surface(surface)
face.add_loops([loop1, loop2, loop3], reverse=False)

# for loop in face.loops:
#     print(loop.loop.Orientation())

brep = BRep.from_faces([face])
mesh = brep.to_tesselation()

# analyzer = ShapeAnalysis_Shell()
# # print(analyzer.CheckOrientedShells(face.face))
# analyzer.LoadShells(face.face)
# print(analyzer.NbLoaded())
# print(analyzer.HasBadEdges())
# print(analyzer.HasConnectedEdges())
# print(analyzer.HasFreeEdges())

viewer = App()
viewer.add(mesh, show_edges=False)

U, V = meshgrid(surface.u_space(), surface.v_space(), "ij")
frames = [surface.frame_at(u, v) for u, v in zip(flatten(U), flatten(V))]
for frame in frames:
    viewer.add(frame, size=0.25)

for edge in brep.edges:
    if edge.is_line:
        viewer.add(edge.to_line(), linewidth=2)
    elif edge.is_circle:
        viewer.add(edge.curve.to_polyline(), linewidth=2)
    elif edge.is_bspline:
        viewer.add(edge.curve.to_polyline(), linewidth=2)

viewer.show()
