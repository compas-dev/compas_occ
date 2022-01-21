import compas.geometry

from typing import Tuple
from typing import List

from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Frame
from compas.geometry import Curve as BaseCurve
from compas.utilities import linspace

from OCC.Core.gp import gp_Pnt
from OCC.Core.gp import gp_Vec
from OCC.Core.Geom import Geom_Curve

from compas_occ.conversions import compas_point_from_occ_point
from compas_occ.conversions import compas_vector_from_occ_vector

Point.from_occ = classmethod(compas_point_from_occ_point)
Vector.from_occ = classmethod(compas_vector_from_occ_vector)


class Curve(BaseCurve):
    """Class representing a general curve object.

    Parameters
    ----------
    name : str, optional
        The name of the curve.

    Attributes
    ----------
    occ_curve : ``Geom_Curve``
        An OCC curve implementing the abstract curve interface.
    domain : tuple[float, float]
        The parameter domain of the curve.
    is_closed
    is_periodic
    is_c0
    is_c1
    is_c2
    is_c3

    """

    def __init__(self, name=None):
        super().__init__(name=name)
        self._occ_curve = None

    @property
    def occ_curve(self) -> Geom_Curve:
        return self._occ_curve

    @occ_curve.setter
    def occ_curve(self, curve: Geom_Curve):
        self._occ_curve = curve

    @property
    def domain(self) -> Tuple[float, float]:
        return self.occ_curve.FirstParameter(), self.occ_curve.LastParameter()

    def point_at(self, t: float) -> compas.geometry.Point:
        """Compute the point at a curve parameter.

        Parameters
        ----------
        t : float
            The curve parameter.

        Returns
        -------
        :class:`compas.geometry.Point`

        """
        start, end = self.domain
        if t < start or t > end:
            raise ValueError("The parameter is not in the domain of the curve.")
        point = self.occ_curve.Value(t)
        return Point.from_occ(point)

    def tangent_at(self, t: float) -> compas.geometry.Vector:
        """Compute the tangent vector at a curve parameter.

        Parameters
        ----------
        t : float
            The curve parameter.

        Returns
        -------
        :class:`compas.geometry.Vector`

        """
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
        :class:`compas.geometry.Vector`

        """
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
        :class:`compas.geometry.Frame`

        """
        point = gp_Pnt()
        uvec = gp_Vec()
        vvec = gp_Vec()
        self.occ_curve.D2(t, point, uvec, vvec)
        return Frame(Point.from_occ(point), Vector.from_occ(uvec), Vector.from_occ(vvec))

    def locus(self, resolution: int = 100) -> List[compas.geometry.Point]:
        """Compute a locus of points along the curve with a given resolution.

        Parameters
        ----------
        resolution : int, optional
            The resolution of the locus.

        Returns
        -------
        list[:class:`compas.geometry.Point`]

        """
        a, b = self.domain
        return [self.point_at(t) for t in linspace(a, b, resolution)]
