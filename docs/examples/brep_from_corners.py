from compas.geometry import Point
from compas_occ.brep import BRep
from compas_view2.app import App

brep3 = BRep.from_corners(Point(0, 0, 0), Point(1, 1, 1), Point(0, 1, 0))
brep4 = BRep.from_corners(Point(0, 2, 0), Point(1, 2, 0), Point(1, 3, 1), Point(0, 3, 0))

viewer = App()
viewer.add(brep3.to_tesselation())
viewer.add(brep4.to_tesselation())
viewer.run()
