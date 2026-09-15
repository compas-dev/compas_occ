from compas_viewer.viewer import Viewer
from OCC.Core import ShapeAnalysis

from compas.colors import Color
from compas.geometry import Box
from compas.geometry import Plane
from compas.geometry import Polygon
from compas.geometry import Polyline
from compas.geometry import Vector
from compas.geometry import offset_polyline
from compas_occ.brep import OCCBrep

polyline = Polyline([[0, 0, 0], [10, 0, 0], [10, 10, 0], [0, 10, 0], [0, 5, 0]])

inside = Polyline(offset_polyline(polyline, 0.05))
outside = Polyline(offset_polyline(polyline, -0.05))

polygon = Polygon(outside.points + inside.points[::-1])

brep = OCCBrep.from_polygons([polygon])
extrusion = OCCBrep.from_extrusion(brep.faces[0], Vector(0, 0, 5))
extrusion.heal()
extrusion.make_solid()

box = Box(10, 1, 3).to_brep()
extrusion = OCCBrep.from_boolean_difference(extrusion, box)

plane = Plane([3, 5, 7.5], [1, 0, 0])
cutter = OCCBrep.from_plane(plane, domain_u=(-10, 10), domain_v=(-10, 10))
extrusion = extrusion.split(cutter)[1]

print(extrusion.is_closed)
print(extrusion.is_orientable)

print(extrusion.is_compound)
print(extrusion.is_solid)
print(extrusion.is_infinite)

closedwires = ShapeAnalysis.ShapeAnalysis_FreeBounds(extrusion.occ_shape).GetClosedWires()
openwires = ShapeAnalysis.ShapeAnalysis_FreeBounds(extrusion.occ_shape).GetOpenWires()

print("Number of closed wires:", closedwires)
print("Number of open wires:", openwires)

viewer = Viewer()
viewer.scene.add(polyline)

viewer.scene.add(inside, color=Color.red())
viewer.scene.add(outside, color=Color.blue())
viewer.scene.add(polygon, color=Color.green())

viewer.scene.add(extrusion, facecolor=Color.cyan(), linecolor=Color.cyan().contrast)

viewer.show()
