from compas_viewer import Viewer

from compas.colors import Color
from compas.geometry import Box
from compas_occ.brep import OCCBrep

box = OCCBrep.from_box(Box(1))

vertex = box.vertices[0]
vertices = box.vertex_neighbors(vertex)
edges = box.vertex_edges(vertex)
faces = box.vertex_faces(vertex)

# =============================================================================
# Visualization
# =============================================================================

viewer = Viewer()

viewer.renderer.camera.target = [0, 0, 0]
viewer.renderer.camera.position = [2, -4, 1]

viewer.scene.add(vertex.point, pointcolor=Color.red(), pointsize=20)

for vertex in vertices:
    viewer.scene.add(vertex.point, pointsize=20)

for edge in edges:
    viewer.scene.add(edge.to_line(), linewidth=5, linecolor=Color(0.2, 0.2, 0.2))

for face in faces:
    brep = OCCBrep.from_brepfaces([face])
    viewer.scene.add(brep, opacity=0.5)

viewer.scene.add(box, linewidth=2, linecolor=Color(0.2, 0.2, 0.2), show_faces=False, show_points=False)

viewer.show()
