from math import sqrt

from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Frame
from compas.geometry import Box
from compas.geometry import distance_point_point

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


class OCCNurbsCurve(NurbsCurve):
    """Class representing a NURBS curve based on the BSplineCurve of the OCC geometry kernel.

    Parameters
    ----------
    name : str, optional
        The name of the curve.

    Examples
    --------
    Curve from points...

    .. code-block:: python

        from compas.geometry import Point
        from compas_occ.geometry import OCCNurbsCurve

        points = [Point(0, 0, 0), Point(3, 6, 0), Point(6, -3, 3), Point(10, 0, 0)]

        curve = OCCNurbsCurve.from_points(points)

    Curve from parameters...

    .. code-block:: python

        from compas.geometry import Point
        from compas_occ.geometry import OCCNurbsCurve

        points = [Point(0, 0, 0), Point(3, 6, 0), Point(6, -3, 3), Point(10, 0, 0)]

        curve = OCCNurbsCurve.from_parameters(
            points=points,
            weights=[1.0, 1.0, 1.0, 1.0],
            knots=[0.0, 1.0],
            multiplicities=[4, 4],
            degree=3
        )
    """

    def __init__(self, name=None):
        super(OCCNurbsCurve, self).__init__(name=name)
        self.occ_curve = None

    def __eq__(self, other: 'OCCNurbsCurve'):
        return self.occ_curve.IsEqual(other.occ_curve)

    # ==============================================================================
    # Data
    # ==============================================================================

    @property
    def data(self):
        """:obj:`dict` - Representation of the curve as a dict containing only native Python objects."""
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
        :class:`OCCNurbsCurve`
        """
        curve = cls()
        curve.occ_curve = occ_curve
        return curve

    @classmethod
    def from_parameters(cls, points, weights, knots, multiplicities, degree, is_periodic=False):
        """Construct a NURBS curve from explicit curve parameters.

        Parameters
        ----------
        points : List[:class:`compas.geometry.Point`]
            The control points.
        weights : List[:obj:`float`]
            The weights of the control points.
        knots : List[:obj:`float`]
            The knots of the curve, without multiplicities.
        multiplicities : List[:obj:`int`]
            The multiplicities of the knots.
        degree : int
            The degree of the curve.
        is_periodic : bool, optional
            Flag indicating that the curve is periodic.

        Returns
        -------
        :class:`OCCNurbsCurve`
        """
        curve = cls()
        curve.occ_curve = occ_curve_from_parameters(points, weights, knots, multiplicities, degree, is_periodic)
        return curve

    @classmethod
    def from_points(cls, points, degree=3):
        """Construct a NURBS curve from control points.

        Parameters
        ----------
        points : List[:class:`compas.geometry.Point`]
            The control points of the curve.
        degree : int, optional
            The degree of the curve.

        Returns
        -------
        :class:`OCCNurbsCurve`
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
        points : List[:class:`compas.geometry.Point`]
            The control points of the curve.
        precision : float, optional
            The precision of the interpolation.

        Returns
        -------
        :class:`OCCNurbsCurve`
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
        :class:`OCCNurbsCurve`
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
        :class:`OCCNurbsCurve`
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
        :class:`OCCNurbsCurve`
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
        :class:`OCCNurbsCurve`
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
        :class:`OCCNurbsCurve`
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
        :class:`OCCNurbsCurve`
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
        """
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
    def occ_shape(self):
        """TopoDS_Shape - The underlying OCC curve embedded in an edge and converted to a shape."""
        return BRepBuilderAPI_MakeEdge(self.occ_curve).Shape()

    @property
    def occ_edge(self):
        """TopoDS_Edge - The underlying OCC curve embedded in an edge."""
        return topods_Edge(self.occ_shape)

    @property
    def occ_points(self):
        """TColgp_Array1OfPnt - The control points of the curve."""
        return self.occ_curve.Poles()

    @property
    def occ_weights(self):
        """TColStd_Array1OfReal - The weights of the control points of the curve."""
        return self.occ_curve.Weights() or array1_from_floats1([1.0] * len(self.occ_points))

    @property
    def occ_knots(self):
        """TColStd_Array1OfReal - The knots of the curve, without multiplicities."""
        return self.occ_curve.Knots()

    @property
    def occ_knotsequence(self):
        """TColStd_Array1OfReal - The full vector of knots of the curve."""
        return self.occ_curve.KnotSequence()

    @property
    def occ_multiplicities(self):
        """TColStd_Array1OfInteger - The multiplicities of the knots of the curve."""
        return self.occ_curve.Multiplicities()

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def points(self):
        """List[:class:`compas.geometry.Point`] - The control points of the curve."""
        if self.occ_curve:
            return points1_from_array1(self.occ_points)

    @property
    def weights(self):
        """List[:obj:`float`] - The weights of the control points of the curve."""
        if self.occ_curve:
            return list(self.occ_weights)

    @property
    def knots(self):
        """List[:obj:`float`] - The knots of the curve, without multiplicities."""
        if self.occ_curve:
            return list(self.occ_knots)

    @property
    def knotsequence(self):
        """List[:obj:`float`] - The full vector of knots of the curve."""
        if self.occ_curve:
            return list(self.occ_knotsequence)

    @property
    def multiplicities(self):
        """List[:obj:`int`] - The multiplicities of the knots of the curve."""
        if self.occ_curve:
            return list(self.occ_multiplicities)

    @property
    def degree(self):
        """:obj:`int` - The degree of the curve."""
        if self.occ_curve:
            return self.occ_curve.Degree()

    @property
    def dimension(self):
        """:obj:`int` - The dimension of the curve."""
        if self.occ_curve:
            return 3

    @property
    def domain(self):
        """Tuple[:obj:`float`, :obj:`float`] - The parameter domain of the curve."""
        if self.occ_curve:
            return self.occ_curve.FirstParameter(), self.occ_curve.LastParameter()

    @property
    def order(self):
        """:obj:`int` - The order of the curve (= degree + 1)."""
        if self.occ_curve:
            return self.degree + 1

    @property
    def start(self):
        """:class:`compas.geometry.Point` - The start point of the curve."""
        if self.occ_curve:
            pnt = self.occ_curve.StartPoint()
            return Point(pnt.X(), pnt.Y(), pnt.Z())

    @property
    def end(self):
        """:class:`compas.geometry.Point` - The end point of the curve."""
        if self.occ_curve:
            pnt = self.occ_curve.EndPoint()
            return Point(pnt.X(), pnt.Y(), pnt.Z())

    @property
    def is_closed(self):
        """:obj:`bool` - Flag indicating that the curve is closed."""
        if self.occ_curve:
            return self.occ_curve.IsClosed()

    @property
    def is_periodic(self):
        """:obj:`bool` - Flag indicating that the curve is periodic."""
        if self.occ_curve:
            return self.occ_curve.IsPeriodic()

    @property
    def is_rational(self):
        """:obj:`bool` - Flag indicating that the curve is rational."""
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
        """Reverse the parametrisation of the curve."""
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
        point : Point
            The point to project to the curve.
        return_parameter : bool, optional
            Return the projected point as well as the curve parameter.

        Returns
        -------
        :class:`compas.geometry.Point`
            The nearest point on the curve, if ``return_parameter`` is false.
        (:class:`compas.geometry.Point`, :obj:`float`)
            The nearest as (point, parameter) tuple, if ``return_parameter`` is true.
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
        curve : :class:`compas_occ.geometry.OCCNurbsCurve`
            The curve to find the closest distance to.
        return_distance : bool, optional
            Return the parameters as well as the minimum distance of the two curves.

        Returns
        -------
        (:obj:`float`, :obj:`float`)
            The parameters on (curve, given curve) as tuple, if ``return_distance`` is false.
        ((:obj:`float`, :obj:`float`), :obj:`float`)
            The (parameters on (curve, given curve), distance) tuple, if ``return_distance`` is true.
        """
        extrema = GeomAPI_ExtremaCurveCurve(self.occ_curve, curve.occ_curve)
        if not return_distance:
            return extrema.LowerDistanceParameters()
        return extrema.LowerDistanceParameters(), extrema.LowerDistance()

    def closest_points_curve(self, curve, return_distance=False):
        """Computes the points on curves where the curve is the closest to another given curve.

        Parameters
        ----------
        curve : NurbsCurve
            The curve to find the closest distance to.
        return_distance : bool, optional
            Return the points as well as the minimum distance of the two curves.

        Returns
        -------
        (:class:`compas.geometry.Point`, :class:`compas.geometry.Point`)
            The points on (curve, given curve) as tuple, if ``return_distance`` is false.
        ((:class:`compas.geometry.Point`, :class:`compas.geometry.Point`), :obj:`float`)
            The (points on (curve, given curve), distance) tuple, if ``return_distance`` is true.
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
        List[:class:`compas_occ.geometry.OCCNurbsCurve`]
        """
        raise NotImplementedError

    def divide_by_length(self, length):
        """Divide the curve into segments of specified length.

        Parameters
        ----------
        length : float

        Returns
        -------
        List[:class:`compas_occ.geometry.OCCNurbsCurve`]
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

    def obb(self, precision: float = 0.0):
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
        :obj:`float`
         """
        return GCPnts_AbscissaPoint_Length(GeomAdaptor_Curve(self.occ_curve))

    def segment(self, u, v, precision=1e-3):
        """Modifies this curve by segmenting it between the parameters u and v.

        Parameters
        ----------
        u: :obj:`float`
        v: :obj:`float`
        tol: :obj:`float`, optional
            Default value is 1e-3

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
        u: :obj:`float`
        v: :obj:`float`
        tol: :obj:`float`, optional
            Default value is 1e-3

        Returns
        -------
        :class:`OCCN`urbsCurve
        """
        copy = self.copy()
        copy.segment(u, v, precision)
        return copy
