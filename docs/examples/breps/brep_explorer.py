# type: ignore
from compas.geometry import Box
from compas.colors import Color
from compas.geometry import Brep
from compas_view2.app import App

box = Box(1).to_brep()

vertex = box.vertices[0]
vertices = box.vertex_neighbors(vertex)
edges = box.vertex_edges(vertex)
faces = box.vertex_faces(vertex)

# =============================================================================
# Visualization
# =============================================================================

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

viewer.add(box, linewidth=2, linecolor=Color(0.2, 0.2, 0.2), show_faces=False)
viewer.show()
