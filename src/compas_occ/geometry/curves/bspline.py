from __future__ import annotations

from typing import List
from compas.geometry import Point
from compas.geometry import Transformation

from compas_occ.interop.arrays import (
    array1_from_points1,
    array1_from_floats1,
    array1_from_integers1,
    points1_from_array1
)

from OCC.Core.gp import gp_Trsf
from OCC.Core.Geom import Geom_BSplineCurve
from OCC.Core.GeomAPI import (
    GeomAPI_Interpolate,
    GeomAPI_PointsToBSpline
)
from OCC.Core.TopoDS import (
    topods_Edge,
    TopoDS_Shape,
    TopoDS_Edge
)
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge

from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.TColStd import (
    TColStd_Array1OfReal,
    TColStd_Array1OfInteger
)
from OCC.Core.Interface import Interface_Static_SetCVal
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.STEPControl import (
    STEPControl_Writer,
    STEPControl_AsIs
)


class BSplineCurve:
    """Wrapper for OCC BSplineCurve."""

    def __init__(self) -> BSplineCurve:
        self.occ_curve = None

    def __eq__(self, other: BSplineCurve) -> bool:
        return self.occ_curve.IsEqual(other.occ_curve)

    @classmethod
    def from_parameters(cls,
                 poles: List[Point],
                 knots: List[float],
                 multiplicities: List[int],
                 degree: int,
                 is_periodic: bool = False) -> BSplineCurve:
        curve = cls()
        curve.occ_curve = Geom_BSplineCurve(
            array1_from_points1(poles),
            array1_from_floats1(knots),
            array1_from_integers1(multiplicities),
            degree,
            is_periodic,
        )
        return curve

    @classmethod
    def from_interpolation(cls, points: List[Point]) -> BSplineCurve:
        curve = cls()
        curve.occ_curve = GeomAPI_Interpolate(array1_from_points1(points)).Curve()
        return curve

    @classmethod
    def from_points(cls, points: List[Point]) -> BSplineCurve:
        curve = cls()
        curve.occ_curve = GeomAPI_PointsToBSpline(array1_from_points1(points)).Curve()
        return curve

    @classmethod
    def from_step(cls, filepath) -> BSplineCurve:
        pass

    def to_step(self, filepath, schema="AP203") -> None:
        step_writer = STEPControl_Writer()
        Interface_Static_SetCVal("write.step.schema", schema)
        step_writer.Transfer(self.occ_edge, STEPControl_AsIs)
        status = step_writer.Write(filepath)
        if status != IFSelect_RetDone:
            raise AssertionError("Operation failed.")

    @property
    def occ_shape(self) -> TopoDS_Shape:
        return BRepBuilderAPI_MakeEdge(self.occ_curve).Shape()

    @property
    def occ_edge(self) -> TopoDS_Edge:
        return topods_Edge(self.occ_shape)

    @property
    def occ_poles(self) -> TColgp_Array1OfPnt:
        return self.occ_curve.Poles()

    @property
    def occ_knots(self) -> TColStd_Array1OfReal:
        return self.occ_curve.Knots()

    @property
    def occ_multiplicities(self) -> TColStd_Array1OfInteger:
        return self.occ_curve.Multiplicities()

    @property
    def poles(self) -> List[Point]:
        return points1_from_array1(self.occ_poles)

    @property
    def knots(self) -> List[float]:
        return self.occ_knots

    @property
    def multiplicities(self) -> List[int]:
        return self.occ_multiplicities

    @property
    def degree(self) -> int:
        return self.occ_curve.Degree()

    @property
    def start(self) -> Point:
        pnt = self.occ_curve.StartPoint()
        return Point(* pnt.XYZ())

    @property
    def end(self) -> Point:
        pnt = self.occ_curve.EndPoint()
        return Point(* pnt.XYZ())

    @property
    def is_closed(self) -> bool:
        return self.occ_curve.IsClosed()

    @property
    def is_periodic(self) -> bool:
        return self.occ_curve.IsPeriodic()

    @property
    def is_rational(self) -> bool:
        return self.occ_curve.IsRational()

    def copy(self):
        return BSplineCurve(self.poles,
                            self.knots,
                            self.multiplicities,
                            self.degree,
                            self.is_periodic)

    def transform(self, T: Transformation) -> None:
        occ_T = gp_Trsf()
        occ_T.SetValues(* T.list)
        self.occ_curve.Transform(occ_T)

    def transformed(self, T: Transformation) -> BSplineCurve:
        copy = self.copy()
        copy.transform(T)
        return copy
