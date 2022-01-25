from typing import Dict, List, Union, Tuple
from compas.geometry import Point
from compas.geometry import Circle

from compas.geometry import NurbsCurve

from OCC.Core.Geom import Geom_BSplineCurve
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.TColStd import TColStd_Array1OfReal
from OCC.Core.TColStd import TColStd_Array1OfInteger


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
    def from_step(cls, filepath: str) -> 'OCCNurbsCurve': ...

    @classmethod
    def from_arc(cls, arc, degree, pointcount=None) -> 'OCCNurbsCurve': ...

    @classmethod
    def from_circle(cls, circle: Circle) -> 'OCCNurbsCurve': ...

    @classmethod
    def from_ellipse(cls, ellipse) -> 'OCCNurbsCurve': ...

    @classmethod
    def from_line(cls, line) -> 'OCCNurbsCurve': ...

    def to_step(self, filepath: str, schema: str = "AP203") -> None: ...

    def to_line(self) -> None: ...

    def to_polyline(self) -> None: ...

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
    def is_rational(self) -> bool: ...

    def closest_point(self, point: Point, return_parameter: bool = False) -> Union[Point, Tuple[Point, float]]: ...

    def closest_parameters_curve(self, curve: 'OCCNurbsCurve', return_distance: bool = False) -> Union[Tuple[float, float], Tuple[Tuple[float, float], float]]: ...

    def closest_points_curve(self, curve: 'OCCNurbsCurve', return_distance: bool = False) -> Union[Tuple[Point, Point], Tuple[Tuple[Point, Point], float]]: ...

    def divide_by_count(self, count) -> List['OCCNurbsCurve']: ...

    def divide_by_length(self, length) -> List['OCCNurbsCurve']: ...

    def segment(self, u: float, v: float, precision: float = 1e-3) -> None: ...

    def segmented(self, u: float, v: float, precision: float = 1e-3) -> 'OCCNurbsCurve': ...
