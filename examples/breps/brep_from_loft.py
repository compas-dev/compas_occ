from compas_viewer import Viewer

from compas.geometry import Circle
from compas.geometry import Frame
from compas.tolerance import TOL
from compas_occ.brep import OCCBrep
from compas_occ.geometry import OCCNurbsCurve

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

curves = [
    OCCNurbsCurve.from_circle(c1),
    OCCNurbsCurve.from_circle(c2),
    OCCNurbsCurve.from_circle(c3),
    OCCNurbsCurve.from_circle(c4),
]

brep = OCCBrep.from_loft(curves)  # type: ignore

TOL.lineardeflection = 1

viewer = Viewer()
viewer.scene.add(brep, linewidth=2)
viewer.show()
