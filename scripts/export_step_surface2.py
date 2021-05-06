from compas.geometry import Point
from compas_occ.geometry.curves.bspline import BSplineCurve

from OCC.Core.GeomFill import GeomFill_BSplineCurves, GeomFill_CoonsStyle

from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.Interface import Interface_Static_SetCVal
from OCC.Core.IFSelect import IFSelect_RetDone

from OCC.Core.TopoDS import topods_Face
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace


points1 = []
points1.append(Point(-4, 0, 2))
points1.append(Point(-7, 2, 2))
points1.append(Point(-6, 3, 1))
points1.append(Point(-4, 3, -1))
points1.append(Point(-3, 5, -2))

spline1 = BSplineCurve.from_points(points1)

points2 = []
points2.append(Point(-4, 0, 2))
points2.append(Point(-2, 2, 0))
points2.append(Point(2, 3, -1))
points2.append(Point(3, 7, -2))
points2.append(Point(4, 9, -1))

spline2 = BSplineCurve.from_points(points2)

fill = GeomFill_BSplineCurves(spline1._occ_curve, spline2._occ_curve, GeomFill_CoonsStyle)
surface = fill.Surface()
face = topods_Face(BRepBuilderAPI_MakeFace(surface, 1e-6).Shape())

step_writer = STEPControl_Writer()
Interface_Static_SetCVal("write.step.schema", "AP203")

step_writer.Transfer(face, STEPControl_AsIs)
status = step_writer.Write("surface1.stp")

if status != IFSelect_RetDone:
	raise AssertionError("load failed")
