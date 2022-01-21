from math import sqrt

from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Frame
from compas.geometry import Box
from compas.geometry import distance_point_point

from compas.geometry import NurbsCurve as BaseNurbsCurve

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
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
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


class NurbsCurve(BaseNurbsCurve):
    """Class representing a NURBS curve based on the BSplineCurve of the OCC geometry kernel.

    Parameters
    ----------
    name : str, optional
        The name of the curve.

    Attributes
    ----------
    occ_curve : Geom_BSplineCurve
        The underlying OCC curve.
    occ_shape : TopoDS_Shape, read-only
        The underlying OCC curve embedded in an edge and converted to a shape.
    occ_edge : TopoDS_Edge, read-only
        The underlying OCC curve embedded in an edge.
    occ_points : TColgp_Array1OfPnt, read-only
        The control points of the curve.
    occ_weights : TColStd_Array1OfReal, read-only
        The weights of the control points of the curve.
    occ_knots : TColStd_Array1OfReal, read-only
        The knots of the curve, without multiplicities.
    occ_knotsequence : TColStd_Array1OfReal, read-only
        The full vector of knots of the curve.
    occ_multiplicities : TColStd_Array1OfInteger, read-only
        The multiplicities of the knots of the curve.
    points : list[:class:`compas.geometry.Point`], read-only
        The control points of the curve.
    weights : list[float], read-only
        The weights of the control points of the curve.
    knots : list[float], read-only
        The knots of the curve, without multiplicities.
    knotsequence : list[float], read-only
        The full vector of knots of the curve.
    multiplicities : list[int], read-only
        The multiplicities of the knots of the curve.
    degree : int, read-only
        The degree of the curve.
    dimension : int, read-only
        The dimension of the curve.
    domain : tuple[float, float], read-only
        The parameter domain of the curve.
    order : int, read-only
        The order of the curve (= degree + 1).
    start : :class:`compas.geometry.Point`, read-only
        The start point of the curve.
    end : :class:`compas.geometry.Point`, read-only
        The end point of the curve.
    is_closed : bool, read-only
        Flag indicating that the curve is closed.
    is_periodic : bool, read-only
        Flag indicating that the curve is periodic.
    is_rational : bool, read-only
        Flag indicating that the curve is rational.

    Examples
    --------
    Curve from points...

    .. code-block:: python

        from compas.geometry import Point
        from compas_occ.geometry import NurbsCurve

        points = [Point(0, 0, 0), Point(3, 6, 0), Point(6, -3, 3), Point(10, 0, 0)]

        curve = NurbsCurve.from_points(points)

    Curve from parameters...

    .. code-block:: python

        from compas.geometry import Point
        from compas_occ.geometry import NurbsCurve

        points = [Point(0, 0, 0), Point(3, 6, 0), Point(6, -3, 3), Point(10, 0, 0)]

        curve = NurbsCurve.from_parameters(
            points=points,
            weights=[1.0, 1.0, 1.0, 1.0],
            knots=[0.0, 1.0],
            multiplicities=[4, 4],
            degree=3
        )

    """

    def __init__(self, name=None):
        super(NurbsCurve, self).__init__(name=name)
        self.occ_curve = None

    def __eq__(self, other: 'NurbsCurve'):
        return self.occ_curve.IsEqual(other.occ_curve)

    # ==============================================================================
    # Data
    # ==============================================================================

    @property
    def data(self):
        """dict - Representation of the curve as a dict containing only native Python objects."""
        return {
            'points': [point.data for point in self.points],
            'weights': self.weights,
            'knots': self.knots,
            'multiplicities': self.multiplicities,
            'degree': self.degree,
            'is_periodic': self.is_periodic
        }

    @data.setter
    def data(self, data):
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
    def from_occ(cls, occ_curve):
        """Construct a NURBS curve from an existing OCC BSplineCurve.

        Parameters
        ----------
        occ_curve : Geom_BSplineCurve

        Returns
        -------
        :class:`NurbsCurve`

        """
        curve = cls()
        curve.occ_curve = occ_curve
        return curve

    @classmethod
    def from_parameters(cls, points, weights, knots, multiplicities, degree, is_periodic=False):
        """Construct a NURBS curve from explicit curve parameters.

        Parameters
        ----------
        points : list[:class:`compas.geometry.Point`]
            The control points.
        weights : list[float]
            The weights of the control points.
        knots : list[float]
            The knots of the curve, without multiplicities.
        multiplicities : list[int]
            The multiplicities of the knots.
        degree : int
            The degree of the curve.
        is_periodic : bool, optional
            Flag indicating that the curve is periodic.

        Returns
        -------
        :class:`NurbsCurve`

        """
        curve = cls()
        curve.occ_curve = occ_curve_from_parameters(points, weights, knots, multiplicities, degree, is_periodic)
        return curve

    @classmethod
    def from_points(cls, points, degree=3):
        """Construct a NURBS curve from control points.

        Parameters
        ----------
        points : list[:class:`compas.geometry.Point`]
            The control points of the curve.
        degree : int, optional
            The degree of the curve.

        Returns
        -------
        :class:`NurbsCurve`

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
    def from_interpolation(cls, points, precision=1e-3):
        """Construct a NURBS curve by interpolating a set of points.

        Parameters
        ----------
        points : list[:class:`compas.geometry.Point`]
            The control points of the curve.
        precision : float, optional
            The precision of the interpolation.

        Returns
        -------
        :class:`NurbsCurve`

        """
        interp = GeomAPI_Interpolate(harray1_from_points1(points), False, precision)
        interp.Perform()
        curve = cls()
        curve.occ_curve = interp.Curve()
        return curve

    @classmethod
    def from_step(cls, filepath):
        """Load a NURBS curve from an STP file.

        Parameters
        ----------
        filepath : str

        Returns
        -------
        :class:`NurbsCurve`

        """
        raise NotImplementedError

    @classmethod
    def from_edge(cls, edge):
        """Construct a NURBS curve from an existing OCC TopoDS_Edge.

        Parameters
        ----------
        edge : TopoDS_Edge
            The OCC edge containing the curve information.

        Returns
        -------
        :class:`NurbsCurve`

        """
        from compas_occ.brep import BRepEdge
        brepedge = BRepEdge(edge)
        if brepedge.is_line:
            line = brepedge.to_line()
            return cls.from_line(line)

    @classmethod
    def from_arc(cls, arc, degree, pointcount=None):
        """Construct a NURBS curve from an arc.

        Parameters
        ----------
        arc : :class:`compas.geometry.Arc`
            The arc geometry.
        degree : int
            The degree of the resulting NURBS curve.
        pointcount : int, optional
            The number of control points in the resulting NURBS curve.

        Returns
        -------
        :class:`NurbsCurve`

        """
        raise NotImplementedError

    @classmethod
    def from_circle(cls, circle):
        """Construct a NURBS curve from a circle.

        Parameters
        ----------
        circle : :class:`compas.geometry.Circle`
            The circle geometry.

        Returns
        -------
        :class:`NurbsCurve`

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

        Parameters
        ----------
        ellipse : :class:`compas.geometry.Ellipse`
            The ellipse geometry.

        Returns
        -------
        :class:`NurbsCurve`

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

        Parameters
        ----------
        line : :class:`compas.geometry.Line`
            The line geometry.

        Returns
        -------
        :class:`NurbsCurve`

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

    def to_step(self, filepath, schema="AP203"):
        """Write the curve geometry to a STP file.

        Parameters
        ----------
        filepath : str
        schema : str, optional

        Returns
        -------
        None

        """
        step_writer = STEPControl_Writer()
        Interface_Static_SetCVal("write.step.schema", schema)
        step_writer.Transfer(self.occ_edge, STEPControl_AsIs)
        status = step_writer.Write(filepath)
        if status != IFSelect_RetDone:
            raise AssertionError("Operation failed.")

    def to_line(self):
        """Convert the geometry to a line.

        Returns
        -------
        :class:`compas.geometry.Line`

        """
        raise NotImplementedError

    def to_polyline(self):
        """Convert the geometry to a polyline.

        Returns
        -------
        :class:`compas.geometry.Polyline`

        """
        raise NotImplementedError

    # ==============================================================================
    # OCC
    # ==============================================================================

    @property
    def occ_shape(self):
        return BRepBuilderAPI_MakeEdge(self.occ_curve).Shape()

    @property
    def occ_edge(self):
        return topods_Edge(self.occ_shape)

    @property
    def occ_points(self):
        return self.occ_curve.Poles()

    @property
    def occ_weights(self):
        return self.occ_curve.Weights() or array1_from_floats1([1.0] * len(self.occ_points))

    @property
    def occ_knots(self):
        return self.occ_curve.Knots()

    @property
    def occ_knotsequence(self):
        return self.occ_curve.KnotSequence()

    @property
    def occ_multiplicities(self):
        return self.occ_curve.Multiplicities()

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def points(self):
        if self.occ_curve:
            return points1_from_array1(self.occ_points)

    @property
    def weights(self):
        if self.occ_curve:
            return list(self.occ_weights)

    @property
    def knots(self):
        if self.occ_curve:
            return list(self.occ_knots)

    @property
    def knotsequence(self):
        if self.occ_curve:
            return list(self.occ_knotsequence)

    @property
    def multiplicities(self):
        if self.occ_curve:
            return list(self.occ_multiplicities)

    @property
    def degree(self):
        if self.occ_curve:
            return self.occ_curve.Degree()

    @property
    def dimension(self):
        if self.occ_curve:
            return 3

    @property
    def domain(self):
        if self.occ_curve:
            return self.occ_curve.FirstParameter(), self.occ_curve.LastParameter()

    @property
    def order(self):
        if self.occ_curve:
            return self.degree + 1

    @property
    def start(self):
        if self.occ_curve:
            pnt = self.occ_curve.StartPoint()
            return Point(pnt.X(), pnt.Y(), pnt.Z())

    @property
    def end(self):
        if self.occ_curve:
            pnt = self.occ_curve.EndPoint()
            return Point(pnt.X(), pnt.Y(), pnt.Z())

    @property
    def is_closed(self):
        if self.occ_curve:
            return self.occ_curve.IsClosed()

    @property
    def is_periodic(self):
        if self.occ_curve:
            return self.occ_curve.IsPeriodic()

    @property
    def is_rational(self):
        if self.occ_curve:
            return self.occ_curve.IsRational()

    # ==============================================================================
    # Methods
    # ==============================================================================

    def transform(self, T):
        """Transform this curve.

        Parameters
        ----------
        T : :class:`compas.geometry.Transformation`

        Returns
        -------
        None

        """
        occ_T = gp_Trsf()
        occ_T.SetValues(* T.list[:12])
        self.occ_curve.Transform(occ_T)

    def reverse(self):
        """Reverse the parametrisation of the curve.

        Returns
        -------
        None

        """
        self.occ_curve.Reverse()

    def point_at(self, t):
        """Compute a point on the curve.

        Parameters
        ----------
        t : float
            The value of the curve parameter. Must be between 0 and 1.

        Returns
        -------
        :class:`compas.geometry.Point`
            the corresponding point on the curve.

        """
        point = self.occ_curve.Value(t)
        return Point(point.X(), point.Y(), point.Z())

    def tangent_at(self, t):
        """Compute the tangent vector at a point on the curve.

        Parameters
        ----------
        t : float
            The value of the curve parameter. Must be between 0 and 1.

        Returns
        -------
        :class:`compas.geometry.Vector`
            The corresponding tangent vector.

        """
        point = gp_Pnt()
        uvec = gp_Vec()
        self.occ_curve.D1(t, point, uvec)
        return Vector.from_occ(uvec)

    def curvature_at(self, t):
        """Compute the curvature at a point on the curve.

        Parameters
        ----------
        t : float
            The value of the curve parameter. Must be between 0 and 1.

        Returns
        -------
        :class:`compas.geometry.Vector`
            The corresponding curvature vector.

        """
        point = gp_Pnt()
        uvec = gp_Vec()
        vvec = gp_Vec()
        self.occ_curve.D2(t, point, uvec, vvec)
        return Vector.from_occ(vvec)

    def frame_at(self, t):
        """Compute the local frame at a point on the curve.

        Parameters
        ----------
        t : float
            The value of the curve parameter. Must be between 0 and 1.

        Returns
        -------
        :class:`compas.geometry.Frame`
            The corresponding local frame.

        """
        point = gp_Pnt()
        uvec = gp_Vec()
        vvec = gp_Vec()
        self.occ_curve.D2(t, point, uvec, vvec)
        return Frame(Point.from_occ(point), Vector.from_occ(uvec), Vector.from_occ(vvec))

    def closest_point(self, point, return_parameter=False):
        """Compute the closest point on the curve to a given point.
        If an orthogonal projection is not possible, the start or end point is returned, whichever is closer.

        Parameters
        ----------
        point : :class:`compas.geometry.Point`
            The point to project to the curve.
        return_parameter : bool, optional
            If True, return the curve parameter in addition to the closest point.

        Returns
        -------
        :class:`compas.geometry.Point` | tuple[:class:`compas.geometry.Point`, float]
            If `return_parameter` is False, the nearest point on the curve.
            If `return_parameter` is True, the nearest point on the curve and the corresponding parameter.

        """
        projector = GeomAPI_ProjectPointOnCurve(point.to_occ(), self.occ_curve)
        try:
            point = Point.from_occ(projector.NearestPoint())
            if return_parameter:
                parameter = projector.LowerDistanceParameter()

        except RuntimeError as e:
            if e.args[0].startswith('StdFail_NotDoneGeomAPI_ProjectPointOnCurve::NearestPoint'):

                start = self.start
                end = self.end

                if distance_point_point(point, start) <= distance_point_point(point, end):
                    point = start
                    if return_parameter:
                        parameter = self.occ_curve.FirstParameter()
                else:
                    point = end
                    if return_parameter:
                        parameter = self.occ_curve.LastParameter()
            else:
                raise

        if not return_parameter:
            return point
        return point, parameter

    def closest_parameters_curve(self, curve, return_distance=False):
        """Computes the curve parameters where the curve is the closest to another given curve.

        Parameters
        ----------
        curve : :class:`compas_occ.geometry.NurbsCurve`
            The curve to find the closest distance to.
        return_distance : bool, optional
            If True, return the minimum distance between the two curves in addition to the curve parameters.

        Returns
        -------
        tuple[float, float] | tuple[tuple[float, float], float]
            If `return_distance` is False, the lowest distance parameters on the two curves.
            If `return_distance` is True, the distance between the two curves in addition to the curve parameters.

        """
        extrema = GeomAPI_ExtremaCurveCurve(self.occ_curve, curve.occ_curve)
        if not return_distance:
            return extrema.LowerDistanceParameters()
        return extrema.LowerDistanceParameters(), extrema.LowerDistance()

    def closest_points_curve(self, curve, return_distance=False):
        """Computes the points on curves where the curve is the closest to another given curve.

        Parameters
        ----------
        curve : :class:`compas_occ.geometry.NurbsCurve`
            The curve to find the closest distance to.
        return_distance : bool, optional
            If True, return the minimum distance between the curves in addition to the closest points.

        Returns
        -------
        tuple[:class:`compas.geometry.Point`, :class:`compas.geometry.Point`] | tuple[tuple[:class:`compas.geometry.Point`, :class:`compas.geometry.Point`], float]
            If `return_distance` is False, the closest points.
            If `return_distance` is True, the distance in addition to the closest points.

        """
        points = (gp_Pnt(), gp_Pnt())
        extrema = GeomAPI_ExtremaCurveCurve(self.occ_curve, curve.occ_curve)
        extrema.NearestPoints(points[0], points[1])
        if not return_distance:
            return (Point.from_occ(points[0]), Point.from_occ(points[1]))
        return (Point.from_occ(points[0]), Point.from_occ(points[1])), extrema.LowerDistance()

    def divide_by_count(self, count):
        """Divide the curve into a specific number of equal length segments.

        Parameters
        ----------
        count : int

        Returns
        -------
        list[:class:`compas_occ.geometry.NurbsCurve`]

        """
        raise NotImplementedError

    def divide_by_length(self, length):
        """Divide the curve into segments of specified length.

        Parameters
        ----------
        length : float

        Returns
        -------
        list[:class:`compas_occ.geometry.NurbsCurve`]

        """
        raise NotImplementedError

    def aabb(self, precision=0.0):
        """Compute the axis aligned bounding box of the curve.

        Parameters
        ----------
        precision : float, optional

        Returns
        -------
        :class:`compas.geometry.Box`

        """
        box = Bnd_Box()
        BndLib_Add3dCurve_Add(GeomAdaptor_Curve(self.occ_curve), precision, box)
        return Box.from_diagonal((
            Point.from_occ(box.CornerMin()),
            Point.from_occ(box.CornerMax())))

    def obb(self, precision=0.0):
        """Compute the oriented bounding box of the curve.

        Parameters
        ----------
        precision : float, optional

        Returns
        -------
        :class:`compas.geometry.Box`

        """
        raise NotImplementedError

    def length(self, precision=1e-3):
        """Compute the length of the curve.

        Parameters
        ----------
        precision : float, optional

        Returns
        -------
        float

        """
        return GCPnts_AbscissaPoint_Length(GeomAdaptor_Curve(self.occ_curve))

    def segment(self, u, v, precision=1e-3):
        """Modifies this curve by segmenting it between the parameters u and v.

        Parameters
        ----------
        u : float
            Start parameter of the segment.
        v : float
            End parameter of the segment.
        precision : float, optional

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

    def segmented(self, u, v, precision=1e-3):
        """Returns a copy of this curve by segmenting it between the parameters u and v.

        Parameters
        ----------
        u : float
            Start parameter of the segment.
        v : float
            End parameter of the segment.
        precision : float, optional

        Returns
        -------
        :class:`NurbsCurve`

        """
        copy = self.copy()
        copy.segment(u, v, precision)
        return copy
