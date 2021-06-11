from compas.geometry import Box
from compas_occ.brep.brep import BRep
from compas_view2.app import App

brep = BRep.from_box(Box.from_width_height_depth(1, 1, 1))

mesh = brep.to_tesselation()

viewer = App()
viewer.add(mesh)
viewer.run()
