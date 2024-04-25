from typing import Tuple

from compas.geometry import Curve
from compas.geometry import Frame
from compas.geometry import Point
from compas.geometry import Polyline
from compas.geometry import Vector
from OCC.Core import BRepBuilderAPI
from OCC.Core import Geom2d
from OCC.Core import IFSelect
from OCC.Core import Interface
from OCC.Core import STEPControl
from OCC.Core import TopoDS
from OCC.Core import gp

from compas_occ.conversions import point2d_to_compas
from compas_occ.conversions import vector2d_to_compas


class OCCCurve2d(Curve):
    """Class representing a general 2D curve object ussually generated through an embedding in a surface.

    Parameters
    ----------
    name : str, optional
        The name of the curve.

    Attributes
    ----------
    dimension : int, read-only
        The dimension of the curve is always 2.
    domain : tuple[float, float], read-only
        The domain of the parameter space of the curve.
    end : :class:`~compas.geometry.Point`, read-only
        The end point of the curve.
    is_closed : bool, read-only
        Flag indicating that the curve is closed.
    is_periodic : bool, read-only
        Flag indicating that the curve is periodic.
    start : :class:`~compas.geometry.Point`, read-only
        The start point of the curve.

    """

    def __init__(self, occ_curve: Geom2d.Geom2d_Curve, name=None):
        super().__init__(name=name)
        self._dimension = 2
        self._occ_curve: Geom2d.Geom2d_Curve = None  # type: ignore
        self.occ_curve = occ_curve

    def __eq__(self, other: "OCCCurve2d") -> bool:
        raise NotImplementedError

    # ==============================================================================
    # Data
    # ==============================================================================

    # ==============================================================================
    # OCC Properties
    # ==============================================================================

    @property
    def occ_curve(self) -> Geom2d.Geom2d_Curve:
        return self._occ_curve

    @occ_curve.setter
    def occ_curve(self, curve: Geom2d.Geom2d_Curve):
        self._occ_curve = curve

    @property
    def occ_shape(self) -> TopoDS.TopoDS_Shape:
        return BRepBuilderAPI.BRepBuilderAPI_MakeEdge2d(self.occ_curve).Shape()

    @property
    def occ_edge(self) -> TopoDS.TopoDS_Edge:
        return TopoDS.topods.Edge(self.occ_shape)

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def domain(self) -> Tuple[float, float]:
        return self.occ_curve.FirstParameter(), self.occ_curve.LastParameter()

    @property
    def start(self) -> Point:
        return self.point_at(self.domain[0])

    @property
    def end(self) -> Point:
        return self.point_at(self.domain[1])

    @property
    def is_closed(self) -> bool:
        return self.occ_curve.IsClosed()

    @property
    def is_periodic(self) -> bool:
        return self.occ_curve.IsPeriodic()

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_occ(cls, occ_curve: Geom2d.Geom2d_Curve) -> "OCCCurve2d":
        """Construct a NURBS curve from an existing OCC BSplineCurve.

        Parameters
        ----------
        occ_curve : Geom2d_Curve

        Returns
        -------
        :class:`OCCCurve2d`

        """
        return cls(occ_curve)

    # ==============================================================================
    # Conversions
    # ==============================================================================

    def to_step(self, filepath: str, schema: str = "AP203") -> None:
        """Write the curve geometry to a STP file.

        Parameters
        ----------
        filepath : str
        schema : str, optional

        Returns
        -------
        None

        """
        step_writer = STEPControl.STEPControl_Writer()
        Interface.Interface_Static.SetCVal("write.step.schema", schema)
        step_writer.Transfer(self.occ_edge, STEPControl.STEPControl_AsIs)
        status = step_writer.Write(filepath)
        if status != IFSelect.IFSelect_RetDone:
            raise AssertionError("Operation failed.")

    def to_polyline(self, n: int = 100) -> Polyline:
        """Convert the curve to a polyline.

        Parameters
        ----------
        n : int, optional
            The number of polyline points.

        Returns
        -------
        :class:`compas.geometry.Polyline`

        """
        return Polyline(self.to_points(n=n))

    # ==============================================================================
    # Methods
    # ==============================================================================

    def copy(self) -> "OCCCurve2d":
        """Make an independent copy of the current curve.

        Returns
        -------
        :class:`OCCCurve2d`

        """
        cls = type(self)
        occ_curve = self.occ_curve.Copy()
        return cls(occ_curve)  # type: ignore (Copy returns Geom2d_Geometry)

    def point_at(self, t: float) -> Point:
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
        start, end = self.domain  # type: ignore (domain could be None if no occ_curve is set)
        if t < start or t > end:
            raise ValueError("The parameter is not in the domain of the curve. t = {}, domain: {}".format(t, self.domain))

        point = self.occ_curve.Value(t)
        return point2d_to_compas(point)

    def tangent_at(self, t: float) -> Vector:
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
        start, end = self.domain  # type: ignore (domain could be None if no occ_curve is set)
        if t < start or t > end:
            raise ValueError("The parameter is not in the domain of the curve.")

        point = gp.gp_Pnt2d()
        uvec = gp.gp_Vec2d()
        self.occ_curve.D1(t, point, uvec)
        return vector2d_to_compas(uvec)

    def curvature_at(self, t: float) -> Vector:
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
        start, end = self.domain  # type: ignore (domain could be None if no occ_curve is set)
        if t < start or t > end:
            raise ValueError("The parameter is not in the domain of the curve.")

        point = gp.gp_Pnt2d()
        uvec = gp.gp_Vec2d()
        vvec = gp.gp_Vec2d()
        self.occ_curve.D2(t, point, uvec, vvec)
        return vector2d_to_compas(vvec)

    def frame_at(self, t: float) -> Frame:
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
        start, end = self.domain  # type: ignore (domain could be None if no occ_curve is set)
        if t < start or t > end:
            raise ValueError("The parameter is not in the domain of the curve.")

        point = gp.gp_Pnt2d()
        uvec = gp.gp_Vec2d()
        vvec = gp.gp_Vec2d()
        self.occ_curve.D2(t, point, uvec, vvec)

        return Frame(
            point2d_to_compas(point),
            vector2d_to_compas(uvec),
            vector2d_to_compas(vvec),
        )
