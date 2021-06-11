from compas.geometry import Sphere
from compas_occ.brep.brep import BRep
from compas_view2.app import App

brep = BRep.from_sphere(Sphere([0, 0, 0], 1))

mesh = brep.to_tesselation()

viewer = App()
viewer.add(mesh)
viewer.run()
