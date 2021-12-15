from typing import Dict, List, Union, Tuple
from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Transformation
from compas.geometry import Frame
from compas.geometry import Circle
from compas.geometry import Box

from compas.geometry import NurbsCurve

from compas_occ.conversions import array1_from_points1
from compas_occ.conversions import array1_from_floats1
from compas_occ.conversions import array1_from_integers1
from compas_occ.conversions import compas_point_from_occ_point
from compas_occ.conversions import compas_point_to_occ_point
from compas_occ.conversions import compas_vector_from_occ_vector
from compas_occ.conversions import compas_vector_to_occ_vector

from OCC.Core.Geom import Geom_BSplineCurve
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.TopoDS import TopoDS_Edge
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.TColStd import TColStd_Array1OfReal
from OCC.Core.TColStd import TColStd_Array1OfInteger

Point.from_occ = classmethod(compas_point_from_occ_point)
Point.to_occ = compas_point_to_occ_point
Vector.from_occ = classmethod(compas_vector_from_occ_vector)
Vector.to_occ = compas_vector_to_occ_vector


def occ_curve_from_parameters(points, weights, knots, multiplicities, degree, is_periodic):
    return Geom_BSplineCurve(
        array1_from_points1(points),
        array1_from_floats1(weights),
        array1_from_floats1(knots),
        array1_from_integers1(multiplicities),
        degree,
        is_periodic,
    )


class OCCNurbsCurve(NurbsCurve):

    def __init__(self, name=None) -> None: ...

    def __eq__(self, other: 'OCCNurbsCurve') -> bool: ...

    # ==============================================================================
    # Data
    # ==============================================================================

    @property
    def data(self) -> Dict: ...

    @data.setter
    def data(self, data: Dict) -> None: ...

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_occ(cls, occ_curve: Geom_BSplineCurve) -> 'OCCNurbsCurve': ...

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
    def from_edge(cls, edge: TopoDS_Edge) -> 'OCCNurbsCurve': ...

    @classmethod
    def from_arc(cls, arc, degree, pointcount=None) -> 'OCCNurbsCurve': ...

    @classmethod
    def from_circle(cls, circle: Circle) -> 'OCCNurbsCurve': ...

    @classmethod
    def from_ellipse(cls, ellipse) -> 'OCCNurbsCurve': ...

    @classmethod
    def from_line(cls, line) -> 'OCCNurbsCurve': ...

    # ==============================================================================
    # Conversions
    # ==============================================================================

    def to_step(self, filepath: str, schema: str = "AP203") -> None: ...

    def to_line(self) -> None: ...

    def to_polyline(self) -> None: ...

    # ==============================================================================
    # OCC
    # ==============================================================================

    @property
    def occ_shape(self) -> TopoDS_Shape: ...

    @property
    def occ_edge(self) -> TopoDS_Edge: ...

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

    # ==============================================================================
    # Properties
    # ==============================================================================

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
    def degree(self) -> int: ...

    @property
    def dimension(self) -> int: ...

    @property
    def domain(self) -> Tuple[float, float]: ...

    @property
    def order(self) -> int: ...

    @property
    def start(self) -> Point: ...

    @property
    def end(self) -> Point: ...

    @property
    def is_closed(self) -> bool: ...

    @property
    def is_periodic(self) -> bool: ...

    @property
    def is_rational(self) -> bool: ...

    # ==============================================================================
    # Methods
    # ==============================================================================

    def transform(self, T: Transformation) -> None: ...

    def reverse(self) -> None: ...

    def point_at(self, t: float) -> Point: ...

    def tangent_at(self, t) -> Vector: ...

    def curvature_at(self, t) -> Vector: ...

    def frame_at(self, t) -> Frame: ...

    def closest_point(self, point: Point, return_parameter: bool = False) -> Union[Point, Tuple[Point, float]]: ...

    def closest_parameters_curve(self, curve: NurbsCurve, return_distance: bool = False) -> Union[Tuple[float, float], Tuple[Tuple[float, float], float]]: ...

    def closest_points_curve(self, curve: NurbsCurve, return_distance: bool = False) -> Union[Tuple[Point, Point], Tuple[Tuple[Point, Point], float]]: ...

    def divide_by_count(self, count) -> List['OCCNurbsCurve']: ...

    def divide_by_length(self, length) -> List['OCCNurbsCurve']: ...

    def aabb(self, precision: float = 0.0) -> Box: ...

    def obb(self, precision: float = 0.0) -> Box: ...

    def length(self, precision: float = 1e-3) -> float: ...

    def segment(self, u: float, v: float, precision: float = 1e-3) -> None: ...

    def segmented(self, u: float, v: float, precision: float = 1e-3) -> 'OCCNurbsCurve': ...
