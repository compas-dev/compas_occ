from compas_viewer.viewer import Viewer

from compas.geometry import Circle
from compas.geometry import Vector
from compas_occ.brep import OCCBrep
from compas_occ.brep import OCCBrepEdge
from compas_occ.geometry import OCCNurbsCurve

circle = Circle(radius=0.3)
curve = OCCNurbsCurve.from_circle(circle)
edge = OCCBrepEdge.from_curve(curve)

brep = OCCBrep.from_extrusion(edge, Vector(0, 0, 10))

viewer = Viewer()
viewer.scene.add(brep)
viewer.show()
