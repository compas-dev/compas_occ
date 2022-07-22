from compas.geometry import Frame
from compas.geometry import Curve
from compas.geometry import Box
from compas.geometry import Polyline
from compas.geometry import distance_point_point


from OCC.Core.gp import gp_Trsf
from OCC.Core.gp import gp_Pnt
from OCC.Core.gp import gp_Vec

from OCC.Core.Geom import Geom_OffsetCurve
from OCC.Core.GeomAdaptor import GeomAdaptor_Curve
from OCC.Core.GCPnts import GCPnts_AbscissaPoint_Length
from OCC.Core.GCPnts import GCPnts_AbscissaPoint
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BndLib import BndLib_Add3dCurve_Add
from OCC.Core.GeomAPI import GeomAPI_ProjectPointOnCurve
from OCC.Core.GeomAPI import GeomAPI_ExtremaCurveCurve
from OCC.Core.TopoDS import topods_Edge
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.Interface import Interface_Static_SetCVal
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.STEPControl import STEPControl_Writer
from OCC.Core.STEPControl import STEPControl_AsIs
from OCC.Core.GeomProjLib import geomprojlib_Project
from OCC.Core.GeomProjLib import geomprojlib_Curve2d

from compas_occ.conversions import compas_point_from_occ_point
from compas_occ.conversions import compas_point_from_occ_point2d
from compas_occ.conversions import compas_vector_from_occ_vector
from compas_occ.conversions import compas_vector_from_occ_vector2d
from compas_occ.conversions import compas_vector_to_occ_direction
from compas_occ.conversions import compas_point_to_occ_point


class OCCCurve(Curve):
    """Class representing a general curve object.

    Parameters
    ----------
    name : str, optional
        The name of the curve.

    Attributes
    ----------
    dimension : int, read-only
        The dimension of the curve.
    domain : tuple[float, float], read-only
        The domain of the parameter space of the curve.
    start : :class:`~compas.geometry.Point`, read-only
        The start point of the curve.
    end : :class:`~compas.geometry.Point`, read-only
        The end point of the curve.
    is_closed : bool, read-only
        Flag indicating that the curve is closed.
    is_periodic : bool, read-only
        Flag indicating that the curve is periodic.

    Other Attributes
    ----------------
    occ_curve : ``Geom_Curve``
        The underlying OCC curve.

    """

    def __init__(self, name=None):
        super().__init__(name=name)
        self._dimension = 3
        self._occ_curve = None

    def __eq__(self, other):
        return self.occ_curve.IsEqual(other.occ_curve)

    # ==============================================================================
    # Data
    # ==============================================================================

    # ==============================================================================
    # OCC Properties
    # ==============================================================================

    @property
    def occ_curve(self):
        return self._occ_curve

    @occ_curve.setter
    def occ_curve(self, curve):
        self._occ_curve = curve

    @property
    def occ_shape(self):
        return BRepBuilderAPI_MakeEdge(self.occ_curve).Shape()

    @property
    def occ_edge(self):
        return topods_Edge(self.occ_shape)

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def dimension(self):
        return self._dimension

    @property
    def domain(self):
        if self.occ_curve:
            return self.occ_curve.FirstParameter(), self.occ_curve.LastParameter()

    @property
    def start(self):
        if self.occ_curve:
            pnt = self.occ_curve.StartPoint()
            return compas_point_from_occ_point(pnt)

    @property
    def end(self):
        if self.occ_curve:
            pnt = self.occ_curve.EndPoint()
            return compas_point_from_occ_point(pnt)

    @property
    def is_closed(self):
        if self.occ_curve:
            return self.occ_curve.IsClosed()

    @property
    def is_periodic(self):
        if self.occ_curve:
            return self.occ_curve.IsPeriodic()

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_occ(cls, occ_curve):
        """Construct a NURBS curve from an existing OCC BSplineCurve.

        Parameters
        ----------
        occ_curve : Geom_Curve

        Returns
        -------
        :class:`OCCCurve`

        """
        curve = cls()
        curve.occ_curve = occ_curve
        return curve

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

    def to_polyline(self, n=100):
        """Convert the curve to a polyline.

        Parameters
        ----------
        n : int, optional
            The number of polyline points.

        Returns
        -------
        :class:`compas.geometry.Polyline`

        """
        return Polyline(self.locus(resolution=n))

    # ==============================================================================
    # Methods
    # ==============================================================================

    def copy(self):
        """Make an independent copy of the current curve.

        Returns
        -------
        :class:`compas_occ.geometry.OCCCurve`

        """
        cls = type(self)
        curve = cls()
        curve.occ_curve = self.occ_curve.Copy()
        curve._dimension = self._dimension
        return curve

    def transform(self, T):
        """Transform this curve.

        Parameters
        ----------
        T : :class:`~compas.geometry.Transformation`

        Returns
        -------
        None

        """
        occ_T = gp_Trsf()
        occ_T.SetValues(*T.list[:12])
        self.occ_curve.Transform(occ_T)

    def reverse(self):
        """Reverse the parametrisation of the curve.

        Returns
        -------
        None

        """
        self.occ_curve.Reverse()

    def point_at(self, t):
        """Compute the point at a curve parameter.

        Parameters
        ----------
        t : float
            The curve parameter.

        Returns
        -------
        :class:`~compas.geometry.Point`

        Raises
        ------
        ValueError
            If the parameter is not in the curve domain.

        """
        start, end = self.domain
        if t < start or t > end:
            raise ValueError(
                "The parameter is not in the domain of the curve. t = {}, domain: {}".format(
                    t, self.domain
                )
            )
        point = self.occ_curve.Value(t)
        if self.dimension == 2:
            return compas_point_from_occ_point2d(point)
        return compas_point_from_occ_point(point)

    def tangent_at(self, t):
        """Compute the tangent vector at a curve parameter.

        Parameters
        ----------
        t : float
            The curve parameter.

        Returns
        -------
        :class:`~compas.geometry.Vector`

        Raises
        ------
        ValueError
            If the parameter is not in the curve domain.

        """
        start, end = self.domain
        if t < start or t > end:
            raise ValueError("The parameter is not in the domain of the curve.")
        point = gp_Pnt()
        uvec = gp_Vec()
        self.occ_curve.D1(t, point, uvec)
        if self.dimension == 2:
            return compas_vector_from_occ_vector2d(uvec)
        return compas_vector_from_occ_vector(uvec)

    def curvature_at(self, t):
        """Compute the curvature vector at a curve parameter.

        Parameters
        ----------
        t : float
            The curve parameter.

        Returns
        -------
        :class:`~compas.geometry.Vector`

        Raises
        ------
        ValueError
            If the parameter is not in the curve domain.

        """
        start, end = self.domain
        if t < start or t > end:
            raise ValueError("The parameter is not in the domain of the curve.")
        point = gp_Pnt()
        uvec = gp_Vec()
        vvec = gp_Vec()
        self.occ_curve.D2(t, point, uvec, vvec)
        if self.dimension == 2:
            return compas_vector_from_occ_vector2d(vvec)
        return compas_vector_from_occ_vector(vvec)

    def frame_at(self, t):
        """Compute the local frame at a curve parameter.

        Parameters
        ----------
        t : float
            The curve parameter.

        Returns
        -------
        :class:`~compas.geometry.Frame`

        Raises
        ------
        ValueError
            If the parameter is not in the curve domain.

        """
        start, end = self.domain
        if t < start or t > end:
            raise ValueError("The parameter is not in the domain of the curve.")
        point = gp_Pnt()
        uvec = gp_Vec()
        vvec = gp_Vec()
        self.occ_curve.D2(t, point, uvec, vvec)
        if self.dimension == 2:
            return Frame(
                compas_point_from_occ_point2d(point),
                compas_vector_from_occ_vector2d(uvec),
                compas_vector_from_occ_vector2d(vvec),
            )
        return Frame(
            compas_point_from_occ_point(point),
            compas_vector_from_occ_vector(uvec),
            compas_vector_from_occ_vector(vvec),
        )

    # ==============================================================================
    # Methods continued
    # ==============================================================================

    def aabb(self, precision=0.0):
        """Compute the axis aligned bounding box of the curve.

        Parameters
        ----------
        precision : float, optional

        Returns
        -------
        :class:`~compas.geometry.Box`

        """
        box = Bnd_Box()
        BndLib_Add3dCurve_Add(GeomAdaptor_Curve(self.occ_curve), precision, box)
        return Box.from_diagonal(
            (
                compas_point_from_occ_point(box.CornerMin()),
                compas_point_from_occ_point(box.CornerMax()),
            )
        )

    def length(self, precision=1e-3):
        """Compute the length of the curve.

        Parameters
        ----------
        precision : float, optional

        Returns
        -------
        float

        """
        return GCPnts_AbscissaPoint_Length(GeomAdaptor_Curve(self.occ_curve), precision)

    def closest_point(self, point, return_parameter=False):
        """Compute the closest point on the curve to a given point.
        If an orthogonal projection is not possible, the start or end point is returned, whichever is closer.

        Parameters
        ----------
        point : :class:`~compas.geometry.Point`
            The point to project to the curve.
        return_parameter : bool, optional
            If True, return the curve parameter in addition to the closest point.

        Returns
        -------
        :class:`~compas.geometry.Point` | tuple[:class:`~compas.geometry.Point`, float]
            If `return_parameter` is False, the nearest point on the curve.
            If `return_parameter` is True, the nearest point on the curve and the corresponding parameter.

        """
        projector = GeomAPI_ProjectPointOnCurve(
            compas_point_to_occ_point(point), self.occ_curve
        )
        try:
            point = compas_point_from_occ_point(projector.NearestPoint())
            if return_parameter:
                parameter = projector.LowerDistanceParameter()
        except RuntimeError as e:
            if e.args[0].startswith(
                "StdFail_NotDoneGeomAPI_ProjectPointOnCurve::NearestPoint"
            ):
                start = self.start
                end = self.end
                if distance_point_point(point, start) <= distance_point_point(
                    point, end
                ):
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
        curve : :class:`~compas_occ.geometry.OCCNurbsCurve`
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
        curve : :class:`~compas_occ.geometry.OCCNurbsCurve`
            The curve to find the closest distance to.
        return_distance : bool, optional
            If True, return the minimum distance between the curves in addition to the closest points.

        Returns
        -------
        tuple[:class:`~compas.geometry.Point`, :class:`~compas.geometry.Point`] | tuple[tuple[:class:`~compas.geometry.Point`, :class:`~compas.geometry.Point`], float]
            If `return_distance` is False, the closest points.
            If `return_distance` is True, the distance in addition to the closest points.

        """
        a, b = gp_Pnt(), gp_Pnt()
        extrema = GeomAPI_ExtremaCurveCurve(self.occ_curve, curve.occ_curve)
        extrema.NearestPoints(a, b)
        points = compas_point_from_occ_point(a), compas_point_from_occ_point(b)
        if not return_distance:
            return points
        return points, extrema.LowerDistance()

    def divide_by_count(self, count, return_points=False, precision=1e-6):
        """Divide the curve into a specific number of equal length segments.

        Parameters
        ----------
        count : int
            The number of segments.
        return_points : bool, optional
            If True, return the list of division parameters,
            and the points corresponding to those parameters.
            If False, return only the list of parameters.

        Returns
        -------
        list[float] | tuple[list[float], list[:class:`~compas.geometry.Point`]]
            If `return_points` is False, the parameters of the discretisation.
            If `return_points` is True, a list of points in addition to the parameters of the discretisation.

        """
        L = self.length(precision=precision)
        length = L / count
        a, b = self.domain
        t = a
        params = [t]
        adaptor = GeomAdaptor_Curve(self.occ_curve)
        for _ in range(count - 1):
            a = GCPnts_AbscissaPoint(adaptor, length, t, precision)
            t = a.Parameter()
            params.append(t)
        params.append(b)
        if not return_points:
            return params
        points = [self.point_at(t) for t in params]
        return params, points

    divide = divide_by_count

    def divide_by_length(self, length, return_points=False, precision=1e-6):
        """"""
        L = self.length(precision=precision)
        count = int(L / length)
        a, b = self.domain
        t = a
        params = [t]
        adaptor = GeomAdaptor_Curve(self.occ_curve)
        for _ in range(count - 1):
            a = GCPnts_AbscissaPoint(adaptor, length, t, precision)
            t = a.Parameter()
            params.append(t)
        params.append(b)
        if not return_points:
            return params
        points = [self.point_at(t) for t in params]
        return params, points

    def projected(self, surface):
        """Return a copy of the curve projected onto a surface.

        Parameters
        ----------
        surface : :class:`compas_occ.geometry.OCCSurface`
            The projection surface.

        Returns
        -------
        :class:`OCCCurve`

        """
        result = geomprojlib_Project(self.occ_curve, surface.occ_surface)
        curve = OCCCurve.from_occ(result)
        return curve

    def embedded(self, surface):
        """Return a copy of the curve embedded in the parameter space of the surface.

        Parameters
        ----------
        surface : :class:`compas_occ.geometry.OCCSurface`
            The projection surface.

        Returns
        -------
        :class:`OCCCurve`

        """
        result = geomprojlib_Curve2d(self.occ_curve, surface.occ_surface)
        curve = OCCCurve.from_occ(result)
        curve._dimension = 2
        return curve

    def offset(self, distance, direction):
        """Offset the curve over the specified distance in the given direction.

        Parameters
        ----------
        distance : float
            The offset distance.
        direction : :class:`compas.geometry.Vector`
            The offset direction.
            Note that this direction defines the normal of the offset plane.
            At every point of the curve, a positive offset ditance
            will generate a corresponding offset point in the direction of
            the cross product vector of the curve tangent and the offset plane normal.

        Returns
        -------
        None

        """
        occ_curve = Geom_OffsetCurve(
            self.occ_curve, distance, compas_vector_to_occ_direction(direction)
        )
        self.occ_curve = occ_curve
