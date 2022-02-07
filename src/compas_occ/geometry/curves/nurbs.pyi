from typing import List
from typing import Dict

from compas.geometry import Point
from compas.geometry import Circle
from compas.geometry import NurbsCurve

from OCC.Core.Geom import Geom_BSplineCurve
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.TColStd import TColStd_Array1OfReal
from OCC.Core.TColStd import TColStd_Array1OfInteger
from OCC.Core.TopoDS import TopoDS_Edge


def occ_curve_from_parameters(points: List[Point],
                              weights: List[float],
                              knots: List[float],
                              multiplicities: List[int],
                              degree: int,
                              is_periodic: bool = False) -> Geom_BSplineCurve: ...


class OCCNurbsCurve(NurbsCurve):

    def __init__(self, name=None) -> None: ...

    def __eq__(self, other: 'OCCNurbsCurve') -> bool: ...

    @property
    def data(self) -> Dict: ...

    @data.setter
    def data(self, data: Dict) -> None: ...

    @property
    def occ_points(self) -> TColgp_Array1OfPnt: ...

    @property
    def occ_weights(self) -> TColStd_Array1OfReal: ...

    @property
    def occ_knots(self) -> TColStd_Array1OfReal: ...

    @property
    def occ_knotsequence(self) -> TColStd_Array1OfReal: ...

    @property
    def occ_multiplicities(self) -> TColStd_Array1OfInteger: ...

    @property
    def points(self) -> List[Point]: ...

    @property
    def weights(self) -> List[float]: ...

    @property
    def knots(self) -> List[float]: ...

    @property
    def knotsequence(self) -> List[float]: ...

    @property
    def multiplicities(self) -> List[int]: ...

    @property
    def continuity(self) -> int: ...

    @property
    def degree(self) -> int: ...

    @property
    def order(self) -> int: ...

    @property
    def is_rational(self) -> bool: ...

    @classmethod
    def from_edge(cls, edge: TopoDS_Edge) -> 'OCCNurbsCurve': ...

    @classmethod
    def from_parameters(cls,
                        points: List[Point],
                        weights: List[float],
                        knots: List[float],
                        multiplicities: List[int],
                        degree: int,
                        is_periodic: bool = False) -> 'OCCNurbsCurve': ...

    @classmethod
    def from_points(cls, points: List[Point], degree: int = 3) -> 'OCCNurbsCurve': ...

    @classmethod
    def from_interpolation(cls, points: List[Point], precision: float = 1e-3) -> 'OCCNurbsCurve': ...

    @classmethod
    def from_arc(cls, arc, degree, pointcount=None) -> 'OCCNurbsCurve': ...

    @classmethod
    def from_circle(cls, circle: Circle) -> 'OCCNurbsCurve': ...

    @classmethod
    def from_ellipse(cls, ellipse) -> 'OCCNurbsCurve': ...

    @classmethod
    def from_line(cls, line) -> 'OCCNurbsCurve': ...

    def segment(self, u: float, v: float, precision: float = 1e-3) -> None: ...

    def segmented(self, u: float, v: float, precision: float = 1e-3) -> 'OCCNurbsCurve': ...
