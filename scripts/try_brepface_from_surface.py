from compas.geometry import Point
from compas.geometry import Circle
from compas.geometry import Plane
from compas.geometry import Vector
from compas_occ.brep import BRepEdge
from compas_occ.geometry import OCCNurbsSurface
from compas_occ.geometry import OCCNurbsCurve
from compas_occ.brep import BRepLoop
from compas_occ.brep import BRepFace
from compas_occ.brep import BRep
from compas_view2.app import App

points = [
    [Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0), Point(3, 0, 0)],
    [Point(0, 1, 0), Point(1, 1, 2), Point(2, 1, 2), Point(3, 1, 0)],
    [Point(0, 2, 0), Point(1, 2, 2), Point(2, 2, 2), Point(3, 2, 0)],
    [Point(0, 3, 0), Point(1, 3, 0), Point(2, 3, 0), Point(3, 3, 0)],
]

surface = OCCNurbsSurface.from_points(points=points)

circle = Circle(Plane(Point(1.5, 1.5, 1.5), Vector(0, 0, 1)), 0.5)
curve = OCCNurbsCurve.from_circle(circle)
curve = curve.projected(surface)
curve = curve.embedded(surface)

edge = BRepEdge.from_curve(curve, surface)
loop = BRepLoop.from_edges([edge])

face = BRepFace.from_surface(surface)
face.add_loop(loop)

brep = BRep.from_faces([face])
mesh = brep.to_tesselation()

viewer = App()
viewer.add(mesh, show_edges=False)
for edge in brep.edges:
    if edge.is_line:
        viewer.add(edge.to_line(), linewidth=2)
    elif edge.is_circle:
        viewer.add(edge.curve.to_polyline(), linewidth=2)
    elif edge.is_bspline:
        viewer.add(edge.curve.to_polyline(), linewidth=2)
viewer.show()
