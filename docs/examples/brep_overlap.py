from compas.geometry import Translation
from compas.geometry import Box
from compas.geometry import Brep
from compas.colors import Color
from compas_view2.app import App
from compas_view2.objects import Collection

box = Box.from_width_height_depth(1, 1, 1)
A = Brep.from_box(box)

box = Box.from_width_height_depth(1, 1, 1)
box.transform(Translation.from_vector([1, 0.3, 0.5]))
B = Brep.from_box(box)

FA, FB = A.overlap(B)

viewer = App()

viewer.add(Collection(items=[A, B]), show_lines=False, opacity=0.5)

brep = Brep.from_native(FA[0].occ_face)
viewer.add(brep, show_lines=False, facecolor=Color.red().lightened(50))

brep = Brep.from_native(FB[0].occ_face)
viewer.add(brep, show_lines=False, facecolor=Color.blue().lightened(50))

viewer.show()
