from compas.geometry import Sphere
from compas_occ.brep import BRep
from compas_view2.app import App

sphere = Sphere([0, 0, 0], 1)

brep = BRep.from_sphere(sphere)

mesh = brep.to_tesselation()

viewer = App()
viewer.add(mesh)
viewer.run()
