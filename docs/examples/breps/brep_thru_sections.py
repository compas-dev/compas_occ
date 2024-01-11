from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections

from compas.geometry import Circle, Frame
from compas_occ.brep import OCCBrepEdge, OCCBrepLoop
from compas.geometry import Brep

from compas_view2.app import App

frame = Frame.worldYZ()
c1 = Circle(1.0, frame=frame)

frame = Frame.worldYZ()
frame.point = [3, 0, 0]
c2 = Circle(3.0, frame=frame)

frame = Frame.worldYZ()
frame.point = [6, 0, 0]
c3 = Circle(0.5, frame=frame)

frame = Frame.worldYZ()
frame.point = [9, 0, 0]
c4 = Circle(3.0, frame=frame)

thru = BRepOffsetAPI_ThruSections(False, False, 1e-6)
thru.AddWire(OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(c1)]).occ_wire)
thru.AddWire(OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(c2)]).occ_wire)
thru.AddWire(OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(c3)]).occ_wire)
thru.AddWire(OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(c4)]).occ_wire)

thru.Build()

brep = Brep.from_native(thru.Shape())

viewer = App()
viewer.add(brep, linewidth=2)
viewer.show()
