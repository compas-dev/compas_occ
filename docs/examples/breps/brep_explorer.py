# type: ignore

from compas.geometry import Box
from compas.colors import Color
from compas.geometry import Brep
from compas_view2.app import App

box = Box.from_width_height_depth(1, 1, 1)
A = Brep.from_box(box)

vertex = A.vertices[0]

vertices = A.vertex_neighbors(vertex)
edges = A.vertex_edges(vertex)
faces = A.vertex_faces(vertex)

viewer = App()
viewer.view.camera.position = [2, -4, 1]
viewer.view.camera.look_at([0, 0, 0])

viewer.add(vertex.point, pointcolor=Color.red(), pointsize=20)

for vertex in vertices:
    viewer.add(vertex.point, pointsize=20)

for edge in edges:
    viewer.add(edge.to_line(), linewidth=5, linecolor=Color(0.2, 0.2, 0.2))

for face in faces:
    brep = Brep.from_brepfaces([face])
    viewer.add(brep, opacity=0.5)

viewer.add(A, linewidth=2, linecolor=Color(0.2, 0.2, 0.2), show_faces=False)

viewer.show()
