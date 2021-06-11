from compas.geometry import Point
from compas_occ.brep.brep import BRep
from compas_view2.app import App

brep3 = BRep.from_corners(Point(0, 0, 0), Point(1, 1, 1), Point(0, 1, 0))
mesh3 = brep3.to_tesselation()

brep4 = BRep.from_corners(Point(0, 2, 0), Point(1, 2, 0), Point(1, 3, 1), Point(0, 3, 0))
mesh4 = brep4.to_tesselation()

viewer = App()
viewer.add(mesh3)
viewer.add(mesh4)
viewer.run()
