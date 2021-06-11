from compas.geometry import Point, Vector, Plane, Circle, Cylinder
from compas_occ.brep.brep import BRep
from compas_view2.app import App

brep = BRep.from_cylinder(Cylinder(Circle(Plane(Point(1, 0, 0), Vector(1, 1, 1)), 1.0), 10.0))

mesh = brep.to_tesselation()

viewer = App()
viewer.add(mesh)
viewer.run()
