from compas.geometry import Vector
from OCC.Core.Geom import Geom_Curve
from OCC.Core.Geom import Geom_SurfaceOfLinearExtrusion

from compas_occ.conversions.geometry import direction_to_occ
from compas_occ.geometry.curves.curve import OCCCurve
from compas_occ.geometry.surfaces.surface import OCCSurface


class OCCExtrusionSurface(OCCSurface):
    """Class representing an extrusion surface based on the corresponding surface of the OCC kernel.

    Note that extrusion surfaces have an infinite parameter space in the "v" direction.

    Parameters
    ----------
    curve : :class:`compas_occ.geometry.OCCCurve`
        The base curve for the extrusion.
        The curve should be planar.
    vector : :class:`compas.geometry.Vector`
        The direction of the extrusion.

    Attributes
    ----------
    curve : :class:`compas_occ.geometry.OCCCurve`
        the base curve for the extrusion.
    vector : :class:`compas.vector.Vector`
        The direction of the extrusion.

    Examples
    --------
    >>>

    """

    def __init__(self, curve, vector=None, **kwargs):
        super().__init__(**kwargs)
        self._curve = None
        self._vector = None
        self.curve = curve
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
        """Compute the extrusion surface using the current curve and direction.

        Returns
        -------
        None

        """
        direction = direction_to_occ(self.vector)
        surface = Geom_SurfaceOfLinearExtrusion(self.curve.occ_curve, direction)  # type: ignore
        self.occ_surface = surface
