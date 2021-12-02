from math import sqrt

from typing import Dict, List, Union, Tuple
from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Transformation
from compas.geometry import Frame
from compas.geometry import Circle
from compas.geometry import Box
from compas.utilities import linspace

from compas.geometry import NurbsCurve

from compas_occ.conversions import harray1_from_points1
from compas_occ.conversions import array1_from_points1
from compas_occ.conversions import array1_from_floats1
from compas_occ.conversions import array1_from_integers1
from compas_occ.conversions import points1_from_array1
from compas_occ.conversions import compas_point_from_occ_point
from compas_occ.conversions import compas_point_to_occ_point
from compas_occ.conversions import compas_vector_from_occ_vector
from compas_occ.conversions import compas_vector_to_occ_vector

from OCC.Core.gp import gp_Trsf
from OCC.Core.gp import gp_Pnt
from OCC.Core.gp import gp_Vec
from OCC.Core.Geom import Geom_BSplineCurve
from OCC.Core.GeomAPI import GeomAPI_Interpolate
from OCC.Core.GeomAPI import GeomAPI_ProjectPointOnCurve
from OCC.Core.GeomAPI import GeomAPI_ExtremaCurveCurve
from OCC.Core.GeomAdaptor import GeomAdaptor_Curve
from OCC.Core.GCPnts import GCPnts_AbscissaPoint_Length
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BndLib import BndLib_Add3dCurve_Add
from OCC.Core.TopoDS import topods_Edge
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.TopoDS import TopoDS_Edge
# from OCC.Core.BRep import BRep_Tool_Curve
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.TColStd import TColStd_Array1OfReal
from OCC.Core.TColStd import TColStd_Array1OfInteger
from OCC.Core.Interface import Interface_Static_SetCVal
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.STEPControl import STEPControl_Writer
from OCC.Core.STEPControl import STEPControl_AsIs

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
        super(OCCNurbsCurve, self).__init__(name=name)
        self.occ_curve = None

    def __eq__(self, other: 'OCCNurbsCurve') -> bool:
        return self.occ_curve.IsEqual(other.occ_curve)

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
        self.occ_curve = occ_curve_from_parameters(points, weights, knots, multiplicities, degree, is_periodic)

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_occ(cls, occ_curve: Geom_BSplineCurve) -> 'OCCNurbsCurve':
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
                        is_periodic: bool = False) -> 'OCCNurbsCurve':
        """Construct a NURBS curve from explicit curve parameters."""
        curve = cls()
        curve.occ_curve = occ_curve_from_parameters(points, weights, knots, multiplicities, degree, is_periodic)
        return curve

    @classmethod
    def from_points(cls, points: List[Point], degree: int = 3) -> 'OCCNurbsCurve':
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
        curve.occ_curve = occ_curve_from_parameters(points, weights, knots, multiplicities, degree, is_periodic)
        return curve

    @classmethod
    def from_interpolation(cls, points: List[Point], precision: float = 1e-3) -> 'OCCNurbsCurve':
        """Construct a NURBS curve by interpolating a set of points.

        This construction method is similar to the method ``CreateHSpline`` of the Rhino API for NURBS curves [1]_.

        References
        ----------
        .. [1] https://developer.rhino3d.com/api/RhinoCommon/html/Overload_Rhino_Geometry_NurbsCurve_CreateHSpline.htm
        .. [2] https://dev.opencascade.org/doc/occt-7.4.0/refman/html/class_geom_a_p_i___interpolate.html

        """
        interp = GeomAPI_Interpolate(harray1_from_points1(points), False, precision)
        interp.Perform()
        curve = cls()
        curve.occ_curve = interp.Curve()
        return curve

    @classmethod
    def from_step(cls, filepath: str) -> 'OCCNurbsCurve':
        """Load a NURBS curve from an STP file."""
        raise NotImplementedError

    @classmethod
    def from_edge(cls, edge: TopoDS_Edge) -> 'OCCNurbsCurve':
        """Construct a NURBS curve from an existing OCC TopoDS_Edge."""
        from compas_occ.brep import BRepEdge
        brepedge = BRepEdge(edge)
        if brepedge.is_line:
            line = brepedge.to_line()
            return cls.from_line(line)

    @classmethod
    def from_arc(cls, arc, degree, pointcount=None) -> 'OCCNurbsCurve':
        raise NotImplementedError

    @classmethod
    def from_circle(cls, circle: Circle) -> 'OCCNurbsCurve':
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
        raise NotImplementedError

    def to_polyline(self):
        raise NotImplementedError

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
    def dimension(self) -> int:
        return 3

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

    def copy(self) -> 'OCCNurbsCurve':
        """Make an independent copy of the current curve."""
        return OCCNurbsCurve.from_parameters(
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

    def transformed(self, T: Transformation) -> 'OCCNurbsCurve':
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

    def point_at(self, t: float) -> Point:
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
        point = self.occ_curve.Value(t)
        return Point(point.X(), point.Y(), point.Z())

    def tangent_at(self, t) -> Vector:
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
        point = gp_Pnt()
        uvec = gp_Vec()
        self.occ_curve.D1(t, point, uvec)
        return Vector.from_occ(uvec)

    def curvature_at(self, t) -> Vector:
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
        point = gp_Pnt()
        uvec = gp_Vec()
        vvec = gp_Vec()
        self.occ_curve.D2(t, point, uvec, vvec)
        return Vector.from_occ(vvec)

    def frame_at(self, t) -> Frame:
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
        point = gp_Pnt()
        uvec = gp_Vec()
        vvec = gp_Vec()
        self.occ_curve.D2(t, point, uvec, vvec)
        return Frame(Point.from_occ(point), Vector.from_occ(uvec), Vector.from_occ(vvec))

    def closest_point(self, point: Point, return_parameter: bool = False) -> Union[Point, Tuple[Point, float]]:
        """Compute the closest point on the curve to a given point.

        Parameters
        ----------
        point : Point
            The point to project orthogonally to the curve.
        return_parameter : bool, optional
            Return the projected point as well as the curve parameter.

        Returns
        -------
        Point or tuple
            The nearest point on the curve, if ``parameter`` is false.
            The nearest as (point, parameter) tuple, if ``parameter`` is true.
        """
        projector = GeomAPI_ProjectPointOnCurve(point.to_occ(), self.occ_curve)
        point = Point.from_occ(projector.NearestPoint())
        if not return_parameter:
            return point
        return point, projector.LowerDistanceParameter()

    def curve_closest_parameters(self, curve: NurbsCurve, return_distance: bool = False) -> Union[Tuple[float, float], Tuple[Tuple[float, float], float]]:
        extrema = GeomAPI_ExtremaCurveCurve(self.occ_curve, curve.occ_curve)
        if not return_distance:
            return extrema.LowerDistanceParameters()
        return extrema.LowerDistanceParameters(), extrema.LowerDistance()

    def divide_by_count(self, count):
        """Divide the curve into a specific number of equal length segments."""
        raise NotImplementedError

    def divide_by_length(self, length):
        """Divide the curve into segments of specified length."""
        raise NotImplementedError

    def aabb(self, precision: float = 0.0) -> Box:
        """Compute the axis aligned bounding box of the curve."""
        box = Bnd_Box()
        BndLib_Add3dCurve_Add(GeomAdaptor_Curve(self.occ_curve), precision, box)
        return Box.from_diagonal((
            Point.from_occ(box.CornerMin()),
            Point.from_occ(box.CornerMax())))

    def obb(self, precision: float = 0.0) -> Box:
        """Compute the oriented bounding box of the curve."""
        raise NotImplementedError

    def length(self, precision: float = 1e-3) -> float:
        """Compute the length of the curve."""
        return GCPnts_AbscissaPoint_Length(GeomAdaptor_Curve(self.occ_curve))

    def segment(self, u: float, v: float, precision: float = 1e-3) -> None:
        """Modifies this curve by segmenting it between the parameters u and v.

        Parameters
        ----------
        u: float
        v: float
        tol: float, optional
            default value is 1e-3

        Returns
        -------
        None

        """
        if u > v:
            u, v = v, u
        s, e = self.domain
        if u < s or v > e:
            raise ValueError('At least one of the given parameters is outside the curve domain.')
        if u == v:
            raise ValueError('The given domain is zero length.')
        self.occ_curve.Segment(u, v, precision)

    def segmented(self, u: float, v: float, precision: float = 1e-3) -> 'OCCNurbsCurve':
        """Returns a copy of this curve by segmenting it between the parameters u and v.

        Parameters
        ----------
        u: float
        v: float
        tol: float,optional
            default value is 1e-3

        Returns
        -------
        NurbsCurve

        """
        copy = self.copy()
        copy.segment(u, v, precision)
        return copy
