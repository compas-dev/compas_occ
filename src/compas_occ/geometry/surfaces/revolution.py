from compas.geometry import Point
from compas.geometry import Vector
from OCC.Core.Geom import Geom_Curve
from OCC.Core.Geom import Geom_SurfaceOfRevolution

from compas_occ.conversions.geometry import axis_to_occ
from compas_occ.geometry.curves.curve import OCCCurve
from compas_occ.geometry.surfaces.surface import OCCSurface


class OCCRevolutionSurface(OCCSurface):
    """Class representing a surface of revolution based on the corresponding surface of the OCC kernel.

    Parameters
    ----------
    curve : :class:`compas_occ.geometry.OCCCurve`
        The base curve for the revolution.
        The curve should be planar.
    point : :class:`compas.geometry.Point`
        The location of the axis of revolution.
    vector : :class:`compas.geometry.Vector`
        The direction of the axis of revolution.

    Attributes
    ----------
    curve : :class:`compas_occ.geometry.OCCCurve`
        The base curve for the revolution.
    point : :class:`compas.geometry.Point`
        The location of the axis of revolution.
    vector : :class:`compas.geometry.Vector`
        The direction of the axis of revolution.

    Examples
    --------
    >>>

    """

    def __init__(self, curve, point=None, vector=None, **kwargs):
        super().__init__(**kwargs)
        self._curve = None
        self._point = None
        self._vector = None
        self.curve = curve
        self.point = point
        self.vector = vector
        self.compute()

    @property
    def curve(self):
        return self._curve

    @curve.setter
    def curve(self, value):
        if isinstance(value, Geom_Curve):
            value = OCCCurve.from_occ(value)
        self._curve = value

    @property
    def point(self):
        if self._point is None:
            self._point = Point(0, 0, 0)
        return self._point

    @point.setter
    def point(self, value):
        if value:
            value = Point(*value)
        self._point = value

    @property
    def vector(self):
        if self._vector is None:
            self._vector = Vector(0, 0, 1)
        return self._vector

    @vector.setter
    def vector(self, value):
        if value:
            value = Vector(*value)
        self._vector = value

    def compute(self):
        """Compute the surface of revolution using the current curve and axis.

        Returns
        -------
        None

        """
        axis = axis_to_occ((self.point, self.vector))
        surface = Geom_SurfaceOfRevolution(self.curve.occ_curve, axis)  # type: ignore
        self.occ_surface = surface
