from compas.geometry import Point
from compas.geometry import Line
from compas.utilities import flatten

from compas_occ.conversions import compas_line_to_occ_line
from compas_occ.conversions import compas_point_from_occ_point
from compas_occ.conversions import compas_point_to_occ_point
from compas_occ.conversions import array2_from_points2
from compas_occ.conversions import array1_from_floats1
from compas_occ.conversions import array2_from_floats2
from compas_occ.conversions import array1_from_integers1
from compas_occ.conversions import floats2_from_array2
from compas_occ.conversions import points2_from_array2

from compas.geometry import NurbsSurface

from OCC.Core.Geom import Geom_BSplineSurface
from OCC.Core.GeomFill import GeomFill_BSplineCurves
from OCC.Core.GeomFill import GeomFill_CoonsStyle

from .surface import OCCSurface


Point.from_occ = classmethod(compas_point_from_occ_point)
Point.to_occ = compas_point_to_occ_point
Line.to_occ = compas_line_to_occ_line


class ControlPoints:
    def __init__(self, surface):
        self.occ_surface = surface

    @property
    def points(self):
        return points2_from_array2(self.occ_surface.Poles())

    def __getitem__(self, index):
        try:
            u, v = index
        except TypeError:
            return self.points[index]
        else:
            pnt = self.occ_surface.Pole(u + 1, v + 1)
            return Point.from_occ(pnt)

    def __setitem__(self, index, point):
        u, v = index
        self.occ_surface.SetPole(u + 1, v + 1, point.to_occ())

    def __len__(self):
        return self.occ_surface.NbVPoles()
        # return self.occ_surface.Poles().NbColumns()

    def __iter__(self):
        return iter(self.points)


class OCCNurbsSurface(OCCSurface, NurbsSurface):
    """Class representing a NURBS surface based on the BSplineSurface of the OCC geometry kernel.

    Parameters
    ----------
    name : str, optional
        The name of the curve

    Attributes
    ----------
    points : list[list[:class:`~compas.geometry.Point`]], read-only
        The control points of the surface.
    weights : list[list[float]], read-only
        The weights of the control points of the surface.
    u_knots : list[float], read-only
        The knots of the surface in the U direction, without multiplicities.
    v_knots : list[float], read-only
        The knots of the surface in the V direction, without multiplicities.
    u_mults : list[int], read-only
        The multiplicities of the knots of the surface in the U direction.
    v_mults : list[int], read-only
        The multiplicities of the knots of the surface in the V direction.

    Other Attributes
    ----------------
    occ_surface : ``Geom_BSplineSurface``
        The underlying OCC surface.

    Examples
    --------
    Construct a surface from points...

    .. code-block:: python

        from compas.geometry import Point
        from compas_occ.geometry import OCCNurbsSurface

        points = [
            [Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0), Point(3, 0, 0)],
            [Point(0, 1, 0), Point(1, 1, 2), Point(2, 1, 2), Point(3, 1, 0)],
            [Point(0, 2, 0), Point(1, 2, 2), Point(2, 2, 2), Point(3, 2, 0)],
            [Point(0, 3, 0), Point(1, 3, 0), Point(2, 3, 0), Point(3, 3, 0)],
        ]

        surface = OCCNurbsSurface.from_points(points=points)

    Construct a surface from points...

    .. code-block:: python

        from compas.geometry import Point
        from compas_occ.geometry import OCCNurbsSurface

        points = [
            [Point(0, 0, 0), Point(1, 0, +0), Point(2, 0, +0), Point(3, 0, +0), Point(4, 0, +0), Point(5, 0, 0)],
            [Point(0, 1, 0), Point(1, 1, -1), Point(2, 1, -1), Point(3, 1, -1), Point(4, 1, -1), Point(5, 1, 0)],
            [Point(0, 2, 0), Point(1, 2, -1), Point(2, 2, +2), Point(3, 2, +2), Point(4, 2, -1), Point(5, 2, 0)],
            [Point(0, 3, 0), Point(1, 3, -1), Point(2, 3, +2), Point(3, 3, +2), Point(4, 3, -1), Point(5, 3, 0)],
            [Point(0, 4, 0), Point(1, 4, -1), Point(2, 4, -1), Point(3, 4, -1), Point(4, 4, -1), Point(5, 4, 0)],
            [Point(0, 5, 0), Point(1, 5, +0), Point(2, 5, +0), Point(3, 5, +0), Point(4, 5, +0), Point(5, 5, 0)],
        ]

        weights = [
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        ]

        surface = OCCNurbsSurface.from_parameters(
            points=points,
            weights=weights,
            u_knots=[1.0, 1 + 1/9, 1 + 2/9, 1 + 3/9, 1 + 4/9, 1 + 5/9, 1 + 6/9, 1 + 7/9, 1 + 8/9, 2.0],
            v_knots=[0.0, 1/9, 2/9, 3/9, 4/9, 5/9, 6/9, 7/9, 8/9, 1.0],
            u_mults=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            v_mults=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            u_degree=3,
            v_degree=3,
        )

    """

    def __init__(self, name=None):
        super().__init__(name=name)
        self._points = None

    def __eq__(self, other):
        for a, b in zip(flatten(self.points), flatten(other.points)):
            if a != b:
                return False
        for a, b in zip(flatten(self.weights), flatten(other.weights)):
            if a != b:
                return False
        for a, b in zip(self.u_knots, self.v_knots):
            if a != b:
                return False
        for a, b in zip(self.u_mults, self.v_mults):
            if a != b:
                return False
        if self.u_degree != self.v_degree:
            return False
        if self.is_u_periodic != self.is_v_periodic:
            return False
        return True

    # ==============================================================================
    # Data
    # ==============================================================================

    @property
    def data(self):
        """dict : Represenation of the surface as a Python dict."""
        return {
            'points': [[point.data for point in row] for row in self.points],
            'weights': self.weights,
            'u_knots': self.u_knots,
            'v_knots': self.v_knots,
            'u_mults': self.u_mults,
            'v_mults': self.v_mults,
            'u_degree': self.u_degree,
            'v_degree': self.v_degree,
            'is_u_periodic': self.is_u_periodic,
            'is_v_periodic': self.is_v_periodic
        }

    @data.setter
    def data(self, data):
        points = [[Point.from_data(point) for point in row] for row in data['points']]
        weights = data['weights']
        u_knots = data['u_knots']
        v_knots = data['v_knots']
        u_mults = data['u_mults']
        v_mults = data['v_mults']
        u_degree = data['u_degree']
        v_degree = data['v_degree']
        is_u_periodic = data['is_u_periodic']
        is_v_periodic = data['is_v_periodic']
        self.occ_surface = Geom_BSplineSurface(
            array2_from_points2(points),
            array1_from_floats1(weights),
            array1_from_floats1(u_knots),
            array1_from_floats1(v_knots),
            array1_from_integers1(u_mults),
            array1_from_integers1(v_mults),
            u_degree,
            v_degree,
            is_u_periodic,
            is_v_periodic
        )

    @classmethod
    def from_data(cls, data):
        """Construct a BSpline surface from its data representation.

        Parameters
        ----------
        data : dict
            The data dictionary.

        Returns
        -------
        :class:`OCCNurbsSurface`
            The constructed surface.

        """
        points = [[Point.from_data(point) for point in row] for row in data['points']]
        weights = data['weights']
        u_knots = data['u_knots']
        v_knots = data['v_knots']
        u_mults = data['u_mults']
        v_mults = data['v_mults']
        u_degree = data['u_degree']
        v_degree = data['v_degree']
        is_u_periodic = data['is_u_periodic']
        is_v_periodic = data['is_v_periodic']
        return OCCNurbsSurface.from_parameters(
            points,
            weights,
            u_knots, v_knots,
            u_mults, v_mults,
            u_degree, v_degree,
            is_u_periodic, is_v_periodic
        )

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_parameters(cls, points, weights, u_knots, v_knots, u_mults, v_mults, u_degree, v_degree, is_u_periodic=False, is_v_periodic=False):
        """Construct a NURBS surface from explicit parameters.

        Parameters
        ----------
        points : list[list[:class:`~compas.geometry.Point`]]
            The control points of the surface.
        weights : list[list[float]]
            The weights of the control points.
        u_knots : list[float]
            The knots in the U direction, without multiplicities.
        v_knots : list[float]
            The knots in the V direction, without multiplicities.
        u_mults : list[int]
            The multiplicities of the knots in the U direction.
        v_mults : list[int]
            The multiplicities of the knots in the V direction.
        u_dergee : int
            Degree in the U direction.
        v_degree : int
            Degree in the V direction.
        is_u_periodic : bool, optional
            Flag indicating that the surface is periodic in the U direction.
        is_v_periodic : bool, optional
            Flag indicating that the surface is periodic in the V direction.

        Returns
        -------
        :class:`OCCNurbsSurface`

        """
        surface = cls()
        surface.occ_surface = Geom_BSplineSurface(
            array2_from_points2(points),
            array2_from_floats2(weights),
            array1_from_floats1(u_knots),
            array1_from_floats1(v_knots),
            array1_from_integers1(u_mults),
            array1_from_integers1(v_mults),
            u_degree,
            v_degree,
            is_u_periodic,
            is_v_periodic
        )
        return surface

    @classmethod
    def from_points(cls, points, u_degree=3, v_degree=3):
        """Construct a NURBS surface from control points.

        Parameters
        ----------
        points : list[list[:class:`~compas.geometry.Point`]]
            The control points.
        u_degree : int, optional
        v_degree : int, optional

        Returns
        -------
        :class:`OCCNurbsSurface`

        """
        u = len(points[0])
        v = len(points)
        weights = [[1.0 for _ in range(u)] for _ in range(v)]
        u_degree = u_degree if u > u_degree else u - 1
        v_degree = v_degree if v > v_degree else v - 1
        u_order = u_degree + 1
        v_order = v_degree + 1
        x = u - u_order
        u_knots = [float(i) for i in range(2 + x)]
        u_mults = [u_order]
        for _ in range(x):
            u_mults.append(1)
        u_mults.append(u_order)
        x = v - v_order
        v_knots = [float(i) for i in range(2 + x)]
        v_mults = [v_order]
        for _ in range(x):
            v_mults.append(1)
        v_mults.append(v_order)
        is_u_periodic = False
        is_v_periodic = False
        return cls.from_parameters(
            points,
            weights,
            u_knots, v_knots,
            u_mults, v_mults,
            u_degree, v_degree,
            is_u_periodic, is_v_periodic
        )

    @classmethod
    def from_step(cls, filepath):
        """Load a NURBS surface from a STP file.

        Parameters
        ----------
        filepath : str

        Returns
        -------
        :class:`OCCNurbsSurface`

        """
        raise NotImplementedError

    @classmethod
    def from_fill(cls, curve1, curve2):
        """Construct a NURBS surface from the infill between two NURBS curves.

        Parameters
        ----------
        curve1 : :class:`~compas_occ.geometry.OCCNurbsCurve`
        curve2 : :class:`~compas_occ.geometry.OCCNurbsCurve`

        Returns
        -------
        :class:`OCCNurbsSurface`

        """
        surface = cls()
        occ_fill = GeomFill_BSplineCurves(curve1.occ_curve, curve2.occ_curve, GeomFill_CoonsStyle)
        surface.occ_surface = occ_fill.Surface()
        return surface

    # ==============================================================================
    # Conversions
    # ==============================================================================

    # ==============================================================================
    # OCC
    # ==============================================================================

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def points(self):
        if not self._points:
            self._points = ControlPoints(self.occ_surface)
        return self._points

    @property
    def weights(self):
        weights = self.occ_surface.Weights()
        if not weights:
            weights = [[1.0] * len(self.points[0]) for _ in range(len(self.points))]
        else:
            weights = floats2_from_array2(weights)
        return weights

    @property
    def u_knots(self):
        return list(self.occ_surface.UKnots())

    @property
    def v_knots(self):
        return list(self.occ_surface.VKnots())

    @property
    def u_mults(self):
        return list(self.occ_surface.UMultiplicities())

    @property
    def v_mults(self):
        return list(self.occ_surface.VMultiplicities())

    # ==============================================================================
    # Methods
    # ==============================================================================
