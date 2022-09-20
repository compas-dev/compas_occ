from compas.geometry import Plane, Circle
from compas_occ.brep import BRepEdge, BRepLoop, BRepFace, BRep
from compas_view2.app import App

plane = Plane.worldXY()

circle1 = Circle(Plane([2, 2, 0], [0, 0, 1]), 1.0)
circle2 = Circle(Plane([-2, -2, 0], [0, 0, 1]), 2.0)
circle3 = Circle(Plane([2, -2, 0], [0, 0, 1]), 0.5)

loop1 = BRepLoop.from_edges([BRepEdge.from_circle(circle1)])
loop2 = BRepLoop.from_edges([BRepEdge.from_circle(circle2)])
loop3 = BRepLoop.from_edges([BRepEdge.from_circle(circle3)])

face = BRepFace.from_plane(plane, udomain=(-5, 5), vdomain=(-5, 5))
face.add_loops([loop1, loop2, loop3], reverse=True)

brep = BRep.from_faces([face])
mesh = brep.to_tesselation()

viewer = App()
viewer.add(mesh, show_lines=False)

for edge in brep.edges:
    if edge.is_line:
        viewer.add(edge.to_line(), linewidth=2)
    elif edge.is_circle:
        viewer.add(edge.curve.to_polyline(), linewidth=2)

viewer.show()
