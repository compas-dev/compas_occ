from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Frame
from compas.geometry import Curve
from compas.geometry import Box

from OCC.Core.gp import gp_Trsf
from OCC.Core.gp import gp_Pnt
from OCC.Core.gp import gp_Vec

from OCC.Core.GeomAdaptor import GeomAdaptor_Curve
from OCC.Core.GCPnts import GCPnts_AbscissaPoint_Length
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BndLib import BndLib_Add3dCurve_Add

from compas_occ.conversions import compas_point_from_occ_point
from compas_occ.conversions import compas_vector_from_occ_vector

Point.from_occ = classmethod(compas_point_from_occ_point)
Vector.from_occ = classmethod(compas_vector_from_occ_vector)


class OCCCurve(Curve):
    """Class representing a general curve object.

    Parameters
    ----------
    name : str, optional
        The name of the curve.

    Attributes
    ----------
    continuity : int, read-only
        The degree of continuity of the curve.
    degree : int, read-only
        The degree of the curve.
    dimension : int, read-only
        The dimension of the curve.
    order : int, read-only
        The order of the curve (= degree + 1).
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
        self._occ_curve = None

    @property
    def occ_curve(self):
        return self._occ_curve

    @occ_curve.setter
    def occ_curve(self, curve):
        self._occ_curve = curve

    # ==============================================================================
    # Data
    # ==============================================================================

    # ==============================================================================
    # Customization
    # ==============================================================================

    def __eq__(self, other):
        return self.occ_curve.IsEqual(other.occ_curve)

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

    # ==============================================================================
    # Conversions
    # ==============================================================================

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def dimension(self):
        if self.occ_curve:
            return 3

    @property
    def continuity(self):
        if self.occ_curve:
            return self.occ_curve.Continuity()

    @property
    def degree(self):
        if self.occ_curve:
            return self.occ_curve.Degree()

    @property
    def domain(self):
        return self.occ_curve.FirstParameter(), self.occ_curve.LastParameter()

    @property
    def order(self):
        if self.occ_curve:
            return self.degree + 1

    @property
    def start(self):
        if self.occ_curve:
            pnt = self.occ_curve.StartPoint()
            return Point.from_occ(pnt)

    @property
    def end(self):
        if self.occ_curve:
            pnt = self.occ_curve.EndPoint()
            return Point.from_occ(pnt)

    @property
    def is_closed(self):
        if self.occ_curve:
            return self.occ_curve.IsClosed()

    @property
    def is_periodic(self):
        if self.occ_curve:
            return self.occ_curve.IsPeriodic()

    # ==============================================================================
    # Methods
    # ==============================================================================

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
            raise ValueError("The parameter is not in the domain of the curve.")
        point = self.occ_curve.Value(t)
        return Point.from_occ(point)

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
        return Vector.from_occ(uvec)

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
        return Vector.from_occ(vvec)

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
        return Frame(Point.from_occ(point), Vector.from_occ(uvec), Vector.from_occ(vvec))

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
        return Box.from_diagonal((
            Point.from_occ(box.CornerMin()),
            Point.from_occ(box.CornerMax())))

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
