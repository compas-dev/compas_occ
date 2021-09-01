from math import sqrt

from typing import Dict, List
from compas.geometry import Point
from compas.geometry import Transformation
from compas.geometry import Frame
from compas.geometry import Circle
from compas.geometry import Box
from compas.utilities import linspace

from compas_occ.conversions import harray1_from_points1
from compas_occ.conversions import array1_from_points1
from compas_occ.conversions import array1_from_floats1
from compas_occ.conversions import array1_from_integers1
from compas_occ.conversions import points1_from_array1
from compas_occ.conversions import compas_point_from_occ_point

from ._curve import Curve

from OCC.Core.gp import gp_Trsf
from OCC.Core.Geom import Geom_BSplineCurve
from OCC.Core.GeomAPI import GeomAPI_Interpolate
from OCC.Core.GeomAdaptor import GeomAdaptor_Curve
from OCC.Core.GCPnts import GCPnts_AbscissaPoint_Length
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BndLib import BndLib_Add3dCurve_Add
from OCC.Core.TopoDS import topods_Edge
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.TopoDS import TopoDS_Edge
from OCC.Core.BRep import BRep_Tool_Curve
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.TColStd import TColStd_Array1OfReal
from OCC.Core.TColStd import TColStd_Array1OfInteger
from OCC.Core.Interface import Interface_Static_SetCVal
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.STEPControl import STEPControl_Writer
from OCC.Core.STEPControl import STEPControl_AsIs

Point.from_occ = classmethod(compas_point_from_occ_point)
# Point.to_occ = compas_point_to_occ_point
# Vector.from_occ = classmethod(compas_vector_from_occ_vector)
# Vector.to_occ = compas_vector_to_occ_vector
# Line.to_occ = compas_line_to_occ_line


class NurbsCurve(Curve):
    """Class representing a NURBS curve based on the BSplineCurve of the OCC geometry kernel.

    Attributes
    ----------
    points: List[Point]
        The control points of the curve.
    weights: List[float]
        The weights of the control points.
    knots: List[float]
        The knot vector, without duplicates.
    multiplicities: List[int]
        The multiplicities of the knots in the knot vector.
    knotsequence: List[float]
        The knot vector, with repeating values according to the multiplicities.
    degree: int
        The degree of the polynomials.
    order: int
        The order of the curve.
    domain: Tuple[float, float]
        The parameter domain.
    start: :class:`Point`
        The point corresponding to the start of the parameter domain.
    end: :class:`Point`
        The point corresponding to the end of the parameter domain.
    is_closed: bool
        True if the curve is closed.
    is_periodic: bool
        True if the curve is periodic.
    is_rational: bool
        True is the curve is rational.

    References
    ----------
    .. [1] https://dev.opencascade.org/doc/occt-7.4.0/refman/html/class_geom___b_spline_curve.html
    .. [2] https://developer.rhino3d.com/api/RhinoCommon/html/T_Rhino_Geometry_NurbsCurve.htm
    .. [3] https://en.wikipedia.org/wiki/Non-uniform_rational_B-spline
    .. [4] https://developer.rhino3d.com/guides/opennurbs/nurbs-geometry-overview/

    """

    @property
    def DATASCHEMA(self):
        from schema import Schema
        from compas.data import is_float3
        from compas.data import is_sequence_of_int
        from compas.data import is_sequence_of_float
        return Schema({
            'points': lambda points: all(is_float3(point) for point in points),
            'weights': is_sequence_of_float,
            'knots': is_sequence_of_float,
            'multiplicities': is_sequence_of_int,
            'degree': int,
            'is_periodic': bool
        })

    @property
    def JSONSCHEMANAME(self):
        raise NotImplementedError

    def __init__(self, name=None) -> None:
        super().__init__(name=name)
        self.occ_curve = None

    def __eq__(self, other: 'NurbsCurve') -> bool:
        return self.occ_curve.IsEqual(other.occ_curve)

    def __str__(self):
        lines = [
            'NurbsCurve',
            '------------',
            f'Points: {self.points}',
            f'Weights: {self.weights}',
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
            'weights': self.weights,
            'knots': self.knots,
            'multiplicities': self.multiplicities,
            'degree': self.degree,
            'is_periodic': self.is_periodic
        }

    @data.setter
    def data(self, data: Dict):
        points = [Point.from_data(point) for point in data['points']]
        weights = data['weights']
        knots = data['knots']
        multiplicities = data['multiplicities']
        degree = data['degree']
        is_periodic = data['is_periodic']
        self.occ_curve = Geom_BSplineCurve(
            array1_from_points1(points),
            array1_from_floats1(weights),
            array1_from_floats1(knots),
            array1_from_integers1(multiplicities),
            degree,
            is_periodic,
        )

    @classmethod
    def from_data(cls, data: Dict) -> 'NurbsCurve':
        """Construct a NURBS curve from its data representation.

        Parameters
        ----------
        data : dict
            The data dictionary.

        Returns
        -------
        :class:`compas_occ.geometry.NurbsCurve`
            The constructed curve.

        """
        points = [Point.from_data(point) for point in data['points']]
        weights = data['weights']
        knots = data['knots']
        multiplicities = data['multiplicities']
        degree = data['degree']
        is_periodic = data['is_periodic']
        return NurbsCurve.from_parameters(points, weights, knots, multiplicities, degree, is_periodic)

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_occ(cls, occ_curve: Geom_BSplineCurve) -> 'NurbsCurve':
        """Construct a NURBS curve from an existing OCC BSplineCurve."""
        curve = cls()
        curve.occ_curve = occ_curve
        return curve

    @classmethod
    def from_parameters(cls,
                        points: List[Point],
                        weights: List[float],
                        knots: List[float],
                        multiplicities: List[int],
                        degree: int,
                        is_periodic: bool = False) -> 'NurbsCurve':
        """Construct a NURBS curve from explicit curve parameters."""
        curve = cls()
        curve.occ_curve = Geom_BSplineCurve(
            array1_from_points1(points),
            array1_from_floats1(weights),
            array1_from_floats1(knots),
            array1_from_integers1(multiplicities),
            degree,
            is_periodic,
        )
        return curve

    @classmethod
    def from_points(cls, points: List[Point], degree: int = 3) -> 'NurbsCurve':
        """Construct a NURBS curve from control points.

        This construction method is similar to the method ``Create`` of the Rhino API for NURBS curves [1]_.

        References
        ----------
        .. [1] https://developer.rhino3d.com/api/RhinoCommon/html/M_Rhino_Geometry_NurbsCurve_Create.htm

        """
        p = len(points)
        weights = [1.0] * p
        degree = degree if p > degree else p - 1
        order = degree + 1
        x = p - order
        knots = [float(i) for i in range(2 + x)]
        multiplicities = [order]
        for _ in range(x):
            multiplicities.append(1)
        multiplicities.append(order)
        is_periodic = False
        curve = cls()
        curve.occ_curve = Geom_BSplineCurve(
            array1_from_points1(points),
            array1_from_floats1(weights),
            array1_from_floats1(knots),
            array1_from_integers1(multiplicities),
            degree,
            is_periodic,
        )
        return curve

    @classmethod
    def from_interpolation(cls, points: List[Point], precision: float = 1e-3) -> 'NurbsCurve':
        """Construct a NURBS curve by interpolating a set of points.

        This construction method is similar to the method ``CreateHSpline`` of the Rhino API for NURBS curves [1]_.

        References
        ----------
        .. [1] https://developer.rhino3d.com/api/RhinoCommon/html/Overload_Rhino_Geometry_NurbsCurve_CreateHSpline.htm
        .. [2] https://dev.opencascade.org/doc/occt-7.4.0/refman/html/class_geom_a_p_i___interpolate.html

        """
        curve = cls()
        interp = GeomAPI_Interpolate(harray1_from_points1(points), False, precision)
        interp.Perform()
        curve.occ_curve = interp.Curve()
        return curve

    @classmethod
    def from_step(cls, filepath: str) -> 'NurbsCurve':
        """Load a NURBS curve from an STP file."""
        pass

    @classmethod
    def from_edge(cls, edge: TopoDS_Edge) -> 'NurbsCurve':
        """Construct a NURBS curve from an existing OCC TopoDS_Edge."""
        res = BRep_Tool_Curve(edge)
        if len(res) != 3:
            return
        return cls.from_occ(res[0])

    @classmethod
    def from_arc(cls, arc, degree, pointcount=None):
        pass

    @classmethod
    def from_circle(cls, circle: Circle) -> 'NurbsCurve':
        """Construct a NURBS curve from a circle.

        This construction method is similar to the method ``CreateFromCircle`` of the Rhino API for NURBS curves [1]_.

        References
        ----------
        .. [1] https://developer.rhino3d.com/api/RhinoCommon/html/Overload_Rhino_Geometry_NurbsCurve_CreateFromCircle.htm

        """
        frame = Frame.from_plane(circle.plane)
        w = 0.5 * sqrt(2)
        dx = frame.xaxis * circle.radius
        dy = frame.yaxis * circle.radius
        points = [
            frame.point - dy,
            frame.point - dy - dx,
            frame.point - dx,
            frame.point + dy - dx,
            frame.point + dy,
            frame.point + dy + dx,
            frame.point + dx,
            frame.point - dy + dx,
            frame.point - dy
        ]
        knots = [0, 1/4, 1/2, 3/4, 1]
        mults = [3, 2, 2, 2, 3]
        weights = [1, w, 1, w, 1, w, 1, w, 1]
        return cls.from_parameters(
            points=points, weights=weights, knots=knots, multiplicities=mults, degree=2
        )

    @classmethod
    def from_ellipse(cls, ellipse):
        """Construct a NURBS curve from an ellipse.

        This construction method is similar to the method ``CreateFromEllipse`` of the Rhino API for NURBS curves [1]_.

        References
        ----------
        .. [1] https://developer.rhino3d.com/api/RhinoCommon/html/Overload_Rhino_Geometry_NurbsCurve_CreateFromEllipse.htm

        """
        frame = Frame.from_plane(ellipse.plane)
        frame = Frame.worldXY()
        w = 0.5 * sqrt(2)
        dx = frame.xaxis * ellipse.major
        dy = frame.yaxis * ellipse.minor
        points = [
            frame.point - dy,
            frame.point - dy - dx,
            frame.point - dx,
            frame.point + dy - dx,
            frame.point + dy,
            frame.point + dy + dx,
            frame.point + dx,
            frame.point - dy + dx,
            frame.point - dy
        ]
        knots = [0, 1/4, 1/2, 3/4, 1]
        mults = [3, 2, 2, 2, 3]
        weights = [1, w, 1, w, 1, w, 1, w, 1]
        return cls.from_parameters(
            points=points, weights=weights, knots=knots, multiplicities=mults, degree=2
        )

    @classmethod
    def from_line(cls, line):
        """Construct a NURBS curve from a line.

        This construction method is similar to the method ``CreateFromLine`` of the Rhino API for NURBS curves [1]_.

        References
        ----------
        .. [1] https://developer.rhino3d.com/api/RhinoCommon/html/Overload_Rhino_Geometry_NurbsCurve_CreateFromLine.htm

        """
        return cls.from_parameters(
            points=[line.start, line.end],
            weights=[1.0, 1.0],
            knots=[0.0, 1.0],
            multiplicities=[2, 2],
            degree=1
        )

    # ==============================================================================
    # Conversions
    # ==============================================================================

    def to_step(self, filepath: str, schema: str = "AP203") -> None:
        """Write the curve geometry to a STP file."""
        step_writer = STEPControl_Writer()
        Interface_Static_SetCVal("write.step.schema", schema)
        step_writer.Transfer(self.occ_edge, STEPControl_AsIs)
        status = step_writer.Write(filepath)
        if status != IFSelect_RetDone:
            raise AssertionError("Operation failed.")

    def to_line(self):
        pass

    def to_polyline(self):
        pass

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
    def occ_points(self) -> TColgp_Array1OfPnt:
        return self.occ_curve.Poles()

    @property
    def occ_weights(self) -> TColStd_Array1OfReal:
        return self.occ_curve.Weights() or array1_from_floats1([1.0] * len(self.occ_points))

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
    def points(self) -> List[Point]:
        return points1_from_array1(self.occ_points)

    @property
    def weights(self) -> List[float]:
        return list(self.occ_weights)

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

    # ==============================================================================
    # Methods
    # ==============================================================================

    def copy(self) -> 'NurbsCurve':
        """Make an independent copy of the current curve."""
        return NurbsCurve.from_parameters(
            self.points,
            self.weights,
            self.knots,
            self.multiplicities,
            self.degree,
            self.is_periodic
        )

    def transform(self, T: Transformation) -> None:
        """Transform this curve."""
        occ_T = gp_Trsf()
        occ_T.SetValues(* T.list)
        self.occ_curve.Transform(occ_T)

    def transformed(self, T: Transformation) -> 'NurbsCurve':
        """Transform a copy of the curve."""
        copy = self.copy()
        copy.transform(T)
        return copy

    def reverse(self) -> None:
        """Reverse the parametrisation of the curve."""
        self.occ_curve.Reverse()

    def space(self, n: int = 10) -> List[float]:
        """Compute evenly spaced parameters over the curve domain."""
        u, v = self.domain
        return linspace(u, v, n)

    def xyz(self, n: int = 10) -> List[Point]:
        """Compute point locations corresponding to evenly spaced parameters over the curve domain."""
        return [self.point_at(param) for param in self.space(n)]

    def locus(self, resolution=100):
        """Compute the locus of the curve.

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
        """Compute the closest point on the curve to a given point."""
        pass

    def divide_by_count(self, count):
        """Divide the curve into a specific number of equal length segments."""
        pass

    def divide_by_length(self, length):
        """Divide the curve into segments of specified length."""
        pass

    def fair(self):
        pass

    def aabb(self, precision: float = 0.0) -> Box:
        """Compute the axis aligned bounding box of the curve."""
        box = Bnd_Box()
        BndLib_Add3dCurve_Add(GeomAdaptor_Curve(self.occ_curve), precision, box)
        return Box.from_diagonal((
            Point.from_occ(box.CornerMin()),
            Point.from_occ(box.CornerMax())
        ))

    def obb(self, precision: float = 0.0) -> Box:
        """Compute the oriented bounding box of the curve."""

    def length(self, precision: float = 1e-3) -> float:
        """Compute the length of the curve."""
        return GCPnts_AbscissaPoint_Length(GeomAdaptor_Curve(self.occ_curve))
