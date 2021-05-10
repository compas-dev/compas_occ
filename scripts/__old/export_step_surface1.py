from OCC.Core.gp import gp_Pnt
from OCC.Core.GeomFill import (
    GeomFill_BSplineCurves,
    GeomFill_CoonsStyle,
)
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline
from OCC.Extend.ShapeFactory import point_list_to_TColgp_Array1OfPnt

from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.Interface import Interface_Static_SetCVal

from OCC.Core.TopoDS import topods_Face
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace


a1 = []
a1.append(gp_Pnt(-4, 0, 2))
a1.append(gp_Pnt(-7, 2, 2))
a1.append(gp_Pnt(-6, 3, 1))
a1.append(gp_Pnt(-4, 3, -1))
a1.append(gp_Pnt(-3, 5, -2))

pt_list1 = point_list_to_TColgp_Array1OfPnt(a1)
SPL1 = GeomAPI_PointsToBSpline(pt_list1).Curve()

a2 = []
a2.append(gp_Pnt(-4, 0, 2))
a2.append(gp_Pnt(-2, 2, 0))
a2.append(gp_Pnt(2, 3, -1))
a2.append(gp_Pnt(3, 7, -2))
a2.append(gp_Pnt(4, 9, -1))

pt_list2 = point_list_to_TColgp_Array1OfPnt(a2)
SPL2 = GeomAPI_PointsToBSpline(pt_list2).Curve()

fill = GeomFill_BSplineCurves(SPL1, SPL2, GeomFill_CoonsStyle)
surface = fill.Surface()
face = topods_Face(BRepBuilderAPI_MakeFace(surface, 1e-6).Shape())

step_writer = STEPControl_Writer()
Interface_Static_SetCVal("write.step.schema", "AP203")

step_writer.Transfer(face, STEPControl_AsIs)
status = step_writer.Write("surface1.stp")
