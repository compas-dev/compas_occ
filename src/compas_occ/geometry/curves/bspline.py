from __future__ import annotations

from typing import List
from compas.geometry import Point
from compas.geometry import Transformation

from compas_occ.interop.arrays import array_of_points, array_of_floats, array_of_integers

from OCC.Core.gp import gp_Trsf
from OCC.Core.Geom import Geom_BSplineCurve
from OCC.Core.GeomAPI import GeomAPI_Interpolate, GeomAPI_PointsToBSpline


class BSplineCurve:
    """Wrapper for OCC BSplineCurve."""

    def __init__(self,
                 poles: List[Point],
                 knots: List[float],
                 multiplicities: List[int],
                 degree: int,
                 is_periodic: bool = False) -> BSplineCurve:
        self._occ_curve = Geom_BSplineCurve(
            array_of_points(poles),
            array_of_floats(knots),
            array_of_integers(multiplicities),
            degree,
            is_periodic,
        )

    @classmethod
    def from_interpolation(cls, points: List[Point]) -> BSplineCurve:
        occ_curve = GeomAPI_Interpolate(array_of_points(points)).Curve()
        poles = [Point(pole.X(), pole.Y(), pole.Z()) for pole in occ_curve.Poles()]
        knots = [float(k) for k in occ_curve.Knots()]
        multiplicities = [int(m) for m in occ_curve.Multiplicities()]
        degree = occ_curve.Degree()
        is_periodic = occ_curve.IsPeriodic()
        return cls(poles, knots, multiplicities, degree, is_periodic)

    @classmethod
    def from_points(cls, points: List[Point]) -> BSplineCurve:
        occ_curve = GeomAPI_PointsToBSpline(array_of_points(points)).Curve()
        poles = [Point(pole.X(), pole.Y(), pole.Z()) for pole in occ_curve.Poles()]
        knots = [float(k) for k in occ_curve.Knots()]
        multiplicities = [int(m) for m in occ_curve.Multiplicities()]
        degree = occ_curve.Degree()
        is_periodic = occ_curve.IsPeriodic()
        return cls(poles, knots, multiplicities, degree, is_periodic)

    @classmethod
    def from_step(cls, filepath):
        pass

    def to_step(self, filepath):
        pass

    def __eq__(self, other: BSplineCurve) -> bool:
        return self._occ_curve.IsEqual(other._occ_curve)

    @property
    def _poles(self):
        return self._occ_curve.Poles()

    @property
    def poles(self):
        return [Point(pole.X(), pole.Y(), pole.Z()) for pole in self._poles]

    @property
    def _weights(self):
        return self._occ_curve.Weights()

    @property
    def weights(self):
        return self._weights

    @property
    def _knots(self):
        return self._occ_curve.Knots()

    @property
    def knots(self):
        return self._knots

    @property
    def _multiplicities(self):
        return self._occ_curve.Multiplicities()

    @property
    def multiplicities(self):
        return self._multiplicities

    @property
    def degree(self) -> int:
        return self._occ_curve.Degree()

    @property
    def start(self) -> Point:
        pnt = self._occ_curve.StartPoint()
        return Point(* pnt.XYZ())

    @property
    def end(self) -> Point:
        pnt = self._occ_curve.EndPoint()
        return Point(* pnt.XYZ())

    @property
    def is_closed(self) -> bool:
        return self._occ_curve.IsClosed()

    @property
    def is_periodic(self) -> bool:
        return self._occ_curve.IsPeriodic()

    @property
    def is_rational(self) -> bool:
        return self._occ_curve.IsRational()

    def copy(self):
        return BSplineCurve(self.poles,
                            self.knots,
                            self.multiplicities,
                            self.degree,
                            self.is_periodic)

    def transform(self, T: Transformation) -> None:
        _T = gp_Trsf()
        _T.SetValues(* T.list)
        self._occ_curve.Transform(T)

    def transformed(self, T: Transformation) -> BSplineCurve:
        copy = self.copy()
        copy.transform(T)
        return copy
