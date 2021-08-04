from __future__ import annotations

from typing import Dict, List
from compas.geometry import Point
from compas.geometry import Transformation
from compas.utilities import linspace

from compas_occ.interop.arrays import (
    harray1_from_points1,
    array1_from_points1,
    array1_from_floats1,
    array1_from_integers1,
    points1_from_array1
)

from ._curve import Curve

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
from OCC.Core.BRep import BRep_Tool_Curve
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


class BSplineCurve(Curve):
    """Wrapper for OCC BSplineCurve."""

    @property
    def DATASCHEMA(self):
        from schema import Schema
        from compas.data import is_float3
        from compas.data import is_sequence_of_int
        from compas.data import is_sequence_of_float
        return Schema({
            'points': lambda points: all(is_float3(point) for point in points),
            'knots': is_sequence_of_float,
            'multiplicities': is_sequence_of_int,
            'degree': int,
            'is_periodic': bool
        })

    @property
    def JSONSCHEMANAME(self):
        raise NotImplementedError

    def __init__(self, name=None) -> BSplineCurve:
        super().__init__(name=name)
        self.occ_curve = None

    def __eq__(self, other: BSplineCurve) -> bool:
        return self.occ_curve.IsEqual(other.occ_curve)

    def __str__(self):
        lines = [
            'BSplineCurve',
            '------------',
            f'Poles: {self.poles}',
            f'Knots: {self.knots}',
            f'Mults: {self.multiplicities}',
            f'Degree: {self.degree}',
            f'Order: {self.order}',
            f'Domain: {self.domain}',
            f'Closed: {self.is_closed}',
            f'Periodic: {self.is_periodic}',
            f'Rational: {self.is_rational}',
        ]
        return "\n".join(lines)

    # ==============================================================================
    # Data
    # ==============================================================================

    @property
    def data(self) -> Dict:
        return {
            'points': [point.data for point in self.points],
            'knots': self.knots,
            'multiplicities': self.multiplicities,
            'degree': self.degree,
            'is_periodic': self.is_periodic
        }

    @data.setter
    def data(self, data: Dict):
        poles = [Point.from_data(point) for point in data['points']]
        knots = data['knots']
        multiplicities = data['multiplicities']
        degree = data['degree']
        is_periodic = data['is_periodic']
        self.occ_curve = Geom_BSplineCurve(
            array1_from_points1(poles),
            array1_from_floats1(knots),
            array1_from_integers1(multiplicities),
            degree,
            is_periodic,
        )

    @classmethod
    def from_data(cls, data: Dict) -> BSplineCurve:
        """Construct a BSpline curve from its data representation.

        Parameters
        ----------
        data : dict
            The data dictionary.

        Returns
        -------
        :class:`compas.geometry.BezierCurve`
            The constructed bezier curve.

        """
        poles = [Point.from_data(point) for point in data['points']]
        knots = data['knots']
        multiplicities = data['multiplicities']
        degree = data['degree']
        is_periodic = data['is_periodic']
        return BSplineCurve.from_parameters(poles, knots, multiplicities, degree, is_periodic)

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_occ(cls, occ_curve: Geom_BSplineCurve) -> BSplineCurve:
        curve = cls()
        curve.occ_curve = occ_curve
        return curve

    @classmethod
    def from_parameters(cls,
                        poles: List[Point],
                        knots: List[float],
                        multiplicities: List[int],
                        degree: int,
                        is_periodic: bool = False) -> BSplineCurve:
        """Construct a curve from poles and knots."""
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
        interp = GeomAPI_Interpolate(harray1_from_points1(points), False, 1e-3)
        interp.Perform()
        curve.occ_curve = interp.Curve()
        return curve

    @classmethod
    def from_points(cls, points: List[Point]) -> BSplineCurve:
        curve = cls()
        curve.occ_curve = GeomAPI_PointsToBSpline(array1_from_points1(points)).Curve()
        return curve

    @classmethod
    def from_step(cls, filepath: str) -> BSplineCurve:
        pass

    @classmethod
    def from_edge(cls, edge: TopoDS_Edge) -> BSplineCurve:
        res = BRep_Tool_Curve(edge)
        if len(res) != 3:
            return
        return cls.from_occ(res[0])

    @classmethod
    def from_arc(cls, arc, degree, pointcount=None):
        pass

    @classmethod
    def from_circle(cls, circle, degree, pointcount=None):
        pass

    @classmethod
    def from_ellipse(cls, ellipse, degree, pointcount=None):
        pass

    @classmethod
    def from_line(cls, line, degree, pointcount=None):
        pass

    # ==============================================================================
    # Conversions
    # ==============================================================================

    def to_step(self, filepath: str, schema: str = "AP203") -> None:
        step_writer = STEPControl_Writer()
        Interface_Static_SetCVal("write.step.schema", schema)
        step_writer.Transfer(self.occ_edge, STEPControl_AsIs)
        status = step_writer.Write(filepath)
        if status != IFSelect_RetDone:
            raise AssertionError("Operation failed.")

    # ==============================================================================
    # OCC
    # ==============================================================================

    @property
    def occ_shape(self) -> TopoDS_Shape:
        return BRepBuilderAPI_MakeEdge(self.occ_curve).Shape()

    @property
    def occ_edge(self) -> TopoDS_Edge:
        return topods_Edge(self.occ_shape)

    @property
    def occ_poles(self) -> TColgp_Array1OfPnt:
        return self.occ_curve.Poles()

    occ_points = occ_poles

    @property
    def occ_knots(self) -> TColStd_Array1OfReal:
        return self.occ_curve.Knots()

    @property
    def occ_knotsequence(self) -> TColStd_Array1OfReal:
        return self.occ_curve.KnotSequence()

    @property
    def occ_multiplicities(self) -> TColStd_Array1OfInteger:
        return self.occ_curve.Multiplicities()

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def poles(self) -> List[Point]:
        return points1_from_array1(self.occ_poles)

    points = poles

    @property
    def knots(self) -> List[float]:
        return list(self.occ_knots)

    @property
    def knotsequence(self) -> List[float]:
        return list(self.occ_knotsequence)

    @property
    def multiplicities(self) -> List[int]:
        return list(self.occ_multiplicities)

    @property
    def degree(self) -> int:
        return self.occ_curve.Degree()

    @property
    def dimension(self):
        pass

    @property
    def domain(self):
        return self.occ_curve.FirstParameter(), self.occ_curve.LastParameter()

    @property
    def order(self):
        return self.degree + 1

    @property
    def start(self) -> Point:
        pnt = self.occ_curve.StartPoint()
        return Point(pnt.X(), pnt.Y(), pnt.Z())

    @property
    def end(self) -> Point:
        pnt = self.occ_curve.EndPoint()
        return Point(pnt.X(), pnt.Y(), pnt.Z())

    @property
    def is_closed(self) -> bool:
        return self.occ_curve.IsClosed()

    @property
    def is_periodic(self) -> bool:
        return self.occ_curve.IsPeriodic()

    @property
    def is_rational(self) -> bool:
        return self.occ_curve.IsRational()

    @property
    def bounding_box(self):
        pass

    @property
    def length(self):
        pass

    # ==============================================================================
    # Methods
    # ==============================================================================

    def copy(self) -> BSplineCurve:
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

    def space(self, n: int = 10) -> List[float]:
        u, v = self.domain
        return linspace(u, v, n)

    def xyz(self, n: int = 10) -> List[Point]:
        return [self.point_at(param) for param in self.space(n)]

    def locus(self, resolution=100):
        """Compute the locus of all points on the curve.

        Parameters
        ----------
        resolution : int
            The number of intervals at which a point on the
            curve should be computed. Defaults to 100.

        Returns
        -------
        list
            Points along the curve.
        """
        return self.xyz(resolution)

    def point_at(self, u: float) -> Point:
        """Compute a point on the curve.

        Parameters
        ----------
        t : float
            The value of the curve parameter. Must be between 0 and 1.

        Returns
        -------
        Point
            the corresponding point on the curve.
        """
        point = self.occ_curve.Value(u)
        return Point(point.X(), point.Y(), point.Z())

    def tangent_at(self, t):
        """Compute the tangent vector at a point on the curve.

        Parameters
        ----------
        t : float
            The value of the curve parameter. Must be between 0 and 1.

        Returns
        -------
        Vector
            The corresponding tangent vector.

        """
        pass

    def curvature_at(self, t):
        """Compute the curvature at a point on the curve.

        Parameters
        ----------
        t : float
            The value of the curve parameter. Must be between 0 and 1.

        Returns
        -------
        Vector
            The corresponding curvature vector.

        """
        pass

    def frame_at(self, t):
        """Compute the local frame at a point on the curve.

        Parameters
        ----------
        t : float
            The value of the curve parameter. Must be between 0 and 1.

        Returns
        -------
        Frame
            The corresponding local frame.

        """
        pass

    def closest_point(self, point, distance=None):
        pass

    def divide_by_count(self, count):
        pass

    def divide_by_length(self, length):
        pass

    def fair(self):
        pass
