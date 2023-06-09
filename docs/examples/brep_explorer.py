from compas.geometry import Box
from compas.colors import Color
from compas.geometry import Brep
from compas_view2.app import App

box = Box.from_width_height_depth(1, 1, 1)
A = Brep.from_box(box)
A.sew()
A.fix()

vertex = A.vertices[0]

vertices = A.vertex_neighbors(vertex)
print(len(vertices))

edges = A.vertex_edges(vertex)
print(len(edges))

faces = A.vertex_faces(vertex)
print(len(faces))

viewer = App()

viewer.add(A, linewidth=1, linecolor=Color(0.2, 0.2, 0.2))

viewer.add(vertex.point, pointcolor=Color.red(), pointsize=20)

for vertex in vertices:
    viewer.add(vertex.point, pointsize=20)

for edge in edges:
    viewer.add(edge.to_line(), linewidth=5, linecolor=Color(0.2, 0.2, 0.2))

for face in faces:
    brep = Brep()
    brep.native_brep = face.occ_face
    viewer.add(brep, show_lines=False, opacity=0.5)

viewer.show()
