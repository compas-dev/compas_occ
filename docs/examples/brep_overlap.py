from compas.geometry import Translation
from compas.geometry import Box
from compas.colors import Color
from compas_occ.brep import BRep
from compas_view2.app import App
from compas_view2.objects import Collection

box = Box.from_width_height_depth(1, 1, 1)
A = BRep.from_box(box)

box = Box.from_width_height_depth(1, 1, 1)
box.transform(Translation.from_vector([1, 0.3, 0.5]))
B = BRep.from_box(box)

FA, FB = A.overlap(B)

viewer = App()

viewmesh = A.to_viewmesh()
viewer.add(viewmesh[0], show_lines=False, opacity=0.5)
viewer.add(Collection(viewmesh[1]), linewidth=3)

viewmesh = B.to_viewmesh()
viewer.add(viewmesh[0], show_lines=False, opacity=0.5)
viewer.add(Collection(viewmesh[1]), linewidth=3)

for face in FA[:1]:
    brep = BRep()
    brep.occ_shape = face.occ_face
    viewmesh = brep.to_viewmesh()
    viewer.add(viewmesh[0], show_lines=False, facecolor=Color.red().lightened(50))
    viewer.add(Collection(viewmesh[1]), linewidth=3, linecolor=Color.red())

for face in FB[:1]:
    brep = BRep()
    brep.occ_shape = face.occ_face
    viewmesh = brep.to_viewmesh()
    viewer.add(viewmesh[0], show_lines=False, facecolor=Color.blue().lightened(50))
    viewer.add(Collection(viewmesh[1]), linewidth=3, linecolor=Color.blue())

viewer.show()
