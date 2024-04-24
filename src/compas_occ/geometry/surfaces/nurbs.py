import warnings
from copy import deepcopy
from typing import Dict
from typing import Iterable
from typing import List
from typing import Literal
from typing import Optional
from typing import Tuple
from typing import Union

from compas.geometry import Curve
from compas.geometry import NurbsSurface
from compas.geometry import Point
from compas.geometry import Translation
from compas.geometry import Vector
from compas.itertools import flatten
from OCC.Core.Geom import Geom_BSplineSurface
from OCC.Core.GeomAbs import GeomAbs_C2
from OCC.Core.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCC.Core.GeomFill import GeomFill_BSplineCurves
from OCC.Core.GeomFill import GeomFill_CoonsStyle
from OCC.Core.GeomFill import GeomFill_CurvedStyle
from OCC.Core.GeomFill import GeomFill_StretchStyle

from compas_occ.conversions import array1_from_floats1
from compas_occ.conversions import array1_from_integers1
from compas_occ.conversions import array2_from_floats2
from compas_occ.conversions import array2_from_points2
from compas_occ.conversions import floats2_from_array2
from compas_occ.conversions import point_to_compas
from compas_occ.conversions import point_to_occ
from compas_occ.conversions import points2_from_array2
from compas_occ.geometry import OCCNurbsCurve

from .surface import OCCSurface


class ControlPoints:
    def __init__(self, surface: "OCCNurbsSurface") -> None:
        self.occ_surface = surface.occ_surface

    @property
    def points(self) -> List[List[Point]]:
        return points2_from_array2(self.occ_surface.Poles())

    def __getitem__(self, index: Union[int, Tuple[int, int]]) -> Point:
        try:
            u, v = index  # type: ignore
        except TypeError:
            return self.points[index]  # type: ignore
        else:
            pnt = self.occ_surface.Pole(u + 1, v + 1)
            return point_to_compas(pnt)

    def __setitem__(self, index: Tuple[int, int], point: Point) -> None:
        u, v = index
        self.occ_surface.SetPole(u + 1, v + 1, point_to_occ(point))

    def __len__(self) -> int:
        return self.occ_surface.NbVPoles()

    def __iter__(self) -> Iterable:
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
    knots_u : list[float], read-only
        The knots of the surface in the U direction, without multiplicities.
    knots_v : list[float], read-only
        The knots of the surface in the V direction, without multiplicities.
    mults_u : list[int], read-only
        The multiplicities of the knots of the surface in the U direction.
    mults_v : list[int], read-only
        The multiplicities of the knots of the surface in the V direction.

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
            knots_u=[1.0, 1 + 1 / 9, 1 + 2 / 9, 1 + 3 / 9, 1 + 4 / 9, 1 + 5 / 9, 1 + 6 / 9, 1 + 7 / 9, 1 + 8 / 9, 2.0],
            knots_v=[0.0, 1 / 9, 2 / 9, 3 / 9, 4 / 9, 5 / 9, 6 / 9, 7 / 9, 8 / 9, 1.0],
            mults_u=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            mults_v=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            degree_u=3,
            degree_v=3,
        )

    """

    _occ_surface: Geom_BSplineSurface

    @property
    def __data__(self) -> Dict:
        return {
            "points": [[point.__data__ for point in row] for row in self.points],  # type: ignore (this seems to be a mypy bug)
            "weights": self.weights,
            "knots_u": self.knots_u,
            "knots_v": self.knots_v,
            "mults_u": self.mults_u,
            "mults_v": self.mults_v,
            "degree_u": self.degree_u,
            "degree_v": self.degree_v,
            "is_periodic_u": self.is_periodic_u,
            "is_periodic_v": self.is_periodic_v,
        }

    @classmethod
    def __from_data__(cls, data: Dict) -> "OCCNurbsSurface":
        points = [[Point.__from_data__(point) for point in row] for row in data["points"]]
        weights = data["weights"]
        knots_u = data["knots_u"]
        knots_v = data["knots_v"]
        mults_u = data["mults_u"]
        mults_v = data["mults_v"]
        degree_u = data["degree_u"]
        degree_v = data["degree_v"]
        is_periodic_u = data["is_periodic_u"]
        is_periodic_v = data["is_periodic_v"]
        return OCCNurbsSurface.from_parameters(
            points,
            weights,
            knots_u,
            knots_v,
            mults_u,
            mults_v,
            degree_u,
            degree_v,
            is_periodic_u,
            is_periodic_v,
        )

    def __init__(self, occ_surface: Geom_BSplineSurface, name: Optional[str] = None) -> None:
        super().__init__(occ_surface, name=name)
        self._points = None
        self.occ_surface = occ_surface

    def __eq__(self, other: "OCCNurbsSurface") -> bool:
        for a, b in zip(flatten(self.points), flatten(other.points)):
            if a != b:
                return False
        for a, b in zip(flatten(self.weights), flatten(other.weights)):
            if a != b:
                return False
        for a, b in zip(self.knots_u, self.knots_v):
            if a != b:
                return False
        for a, b in zip(self.mults_u, self.mults_v):
            if a != b:
                return False
        if self.degree_u != self.degree_v:
            return False
        if self.is_periodic_u != self.is_periodic_v:
            return False
        return True

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_parameters(
        cls,
        points: List[List[Point]],
        weights: List[List[float]],
        knots_u: List[float],
        knots_v: List[float],
        mults_u: List[int],
        mults_v: List[int],
        degree_u: int,
        degree_v: int,
        is_periodic_u: bool = False,
        is_periodic_v: bool = False,
    ) -> "OCCNurbsSurface":
        """Construct a NURBS surface from explicit parameters.

        Parameters
        ----------
        points : list[list[:class:`~compas.geometry.Point`]]
            The control points of the surface.
        weights : list[list[float]]
            The weights of the control points.
        knots_u : list[float]
            The knots in the U direction, without multiplicities.
        knots_v : list[float]
            The knots in the V direction, without multiplicities.
        mults_u : list[int]
            The multiplicities of the knots in the U direction.
        mults_v : list[int]
            The multiplicities of the knots in the V direction.
        u_dergee : int
            Degree in the U direction.
        degree_v : int
            Degree in the V direction.
        is_periodic_u : bool, optional
            Flag indicating that the surface is periodic in the U direction.
        is_periodic_v : bool, optional
            Flag indicating that the surface is periodic in the V direction.

        Returns
        -------
        :class:`OCCNurbsSurface`

        """
        occ_surface = Geom_BSplineSurface(
            array2_from_points2(points),
            array2_from_floats2(weights),
            array1_from_floats1(knots_u),
            array1_from_floats1(knots_v),
            array1_from_integers1(mults_u),
            array1_from_integers1(mults_v),
            degree_u,
            degree_v,
            is_periodic_u,
            is_periodic_v,
        )
        return cls(occ_surface)

    @classmethod
    def from_points(
        cls,
        points: List[List[Point]],
        degree_u: int = 3,
        degree_v: int = 3,
    ) -> "OCCNurbsSurface":
        """Construct a NURBS surface from control points.

        Parameters
        ----------
        points : list[list[:class:`~compas.geometry.Point`]]
            The control points.
        degree_u : int, optional
        degree_v : int, optional

        Returns
        -------
        :class:`OCCNurbsSurface`

        """
        u = len(points[0])
        v = len(points)
        weights = [[1.0 for _ in range(u)] for _ in range(v)]
        degree_u = degree_u if u > degree_u else u - 1
        degree_v = degree_v if v > degree_v else v - 1
        u_order = degree_u + 1
        v_order = degree_v + 1
        x = u - u_order
        knots_u = [float(i) for i in range(2 + x)]
        mults_u = [u_order]
        for _ in range(x):
            mults_u.append(1)
        mults_u.append(u_order)
        x = v - v_order
        knots_v = [float(i) for i in range(2 + x)]
        mults_v = [v_order]
        for _ in range(x):
            mults_v.append(1)
        mults_v.append(v_order)
        is_periodic_u = False
        is_periodic_v = False
        return cls.from_parameters(
            points,
            weights,
            knots_u,
            knots_v,
            mults_u,
            mults_v,
            degree_u,
            degree_v,
            is_periodic_u,
            is_periodic_v,
        )

    @classmethod
    def from_step(cls, filepath: str) -> "OCCNurbsSurface":
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
    def from_fill(
        cls,
        curve1: OCCNurbsCurve,
        curve2: OCCNurbsCurve,
        curve3: Optional[OCCNurbsCurve] = None,
        curve4: Optional[OCCNurbsCurve] = None,
        style: Literal["stretch", "coons", "curved"] = "stretch",
    ) -> "OCCNurbsSurface":
        """Construct a NURBS surface from the infill between two, three or four contiguous NURBS curves.

        Parameters
        ----------
        curve1 : :class:`~compas_occ.geometry.OCCNurbsCurve`
        curve2 : :class:`~compas_occ.geometry.OCCNurbsCurve`
        curve3 : :class:`~compas_occ.geometry.OCCNurbsCurve`, optional.
        curve4 : :class:`~compas_occ.geometry.OCCNurbsCurve`, optional.
        style : Literal['stretch', 'coons', 'curved'], optional.

            * ``'stretch'`` produces the flattest patch.
            * ``'curved'`` produces a rounded patch.
            * ``'coons'`` is between stretch and coons.

        Raises
        ------
        ValueError
            If the fill style is not supported.

        Returns
        -------
        :class:`OCCNurbsSurface`

        """

        if style == "stretch":
            occ_style = GeomFill_StretchStyle
        elif style == "coons":
            occ_style = GeomFill_CoonsStyle
        elif style == "curved":
            occ_style = GeomFill_CurvedStyle
        else:
            warnings.warn('This fill style is not supported: {}. We will use GeomFill_StretchStyle ("stretch") instead.'.format(style))
            occ_style = GeomFill_StretchStyle

        if curve3 and curve4:
            occ_fill = GeomFill_BSplineCurves(
                curve1.occ_curve,
                curve2.occ_curve,
                curve3.occ_curve,
                curve4.occ_curve,
                occ_style,
            )
        elif curve3:
            occ_fill = GeomFill_BSplineCurves(
                curve1.occ_curve,
                curve2.occ_curve,
                curve3.occ_curve,
                occ_style,
            )
        else:
            occ_fill = GeomFill_BSplineCurves(
                curve1.occ_curve,
                curve2.occ_curve,
                occ_style,
            )
        occ_surface = occ_fill.Surface()
        return cls(occ_surface)

    @classmethod
    def from_extrusion(cls, curve: Curve, vector: Vector) -> "OCCNurbsSurface":
        """Construct a NURBS surface from an extrusion of a basis curve.

        Note that the extrusion surface is constructed by generating an infill
        between the basis curve and a translated copy with :meth:`from_fill`.

        Parameters
        ----------
        curve : :class:`compas_occ.geometry.Curve`
            The basis curve for the extrusion.
        vector : :class:`compas.geometry.Vector`
            The extrusion vector, which serves as a translation vector for the basis curve.

        Returns
        -------
        :class:`OCCNurbsSurface`

        """
        other = curve.transformed(Translation.from_vector(vector))
        return cls.from_fill(curve, other)  # type: ignore (not sure how to solve this)

    @classmethod
    def from_interpolation(cls, points: List[List[Point]], precision: float = 1e-3) -> "OCCNurbsSurface":
        """Construct a NURBS surface by approximating or interpolating a 2D collection of points.

        Parameters
        ----------
        points : [list[:class:`compas.geometry.Point`], list[:class:`compas.geometry.Point`]]
            The 2D collection of points.
        precision : float, optional
            The fitting precision.

        Returns
        -------
        :class:`OCCNurbsSurface`

        """
        occ_surface = GeomAPI_PointsToBSplineSurface(
            array2_from_points2(points),
            3,
            8,
            GeomAbs_C2,
            precision,
        ).Surface()
        return cls(occ_surface)

    # ==============================================================================
    # Conversions
    # ==============================================================================

    # ==============================================================================
    # OCC
    # ==============================================================================

    @property
    def occ_surface(self) -> Geom_BSplineSurface:
        return self._occ_surface

    @occ_surface.setter
    def occ_surface(self, surface: Geom_BSplineSurface) -> None:
        self._occ_surface = surface

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def points(self) -> ControlPoints:
        if not self._points:
            self._points = ControlPoints(self)
        return self._points

    @property
    def weights(self) -> List[List[float]]:
        weights = self.occ_surface.Weights()
        if not weights:
            rows = len(self.points)
            cols = len(self.points[0])
            weights = [[1.0] * cols for _ in range(rows)]
        else:
            weights = floats2_from_array2(weights)
        return weights  # type: ignore (not sure what this is about)

    @property
    def degree_u(self) -> int:
        return self.occ_surface.UDegree()

    @property
    def degree_v(self) -> int:
        return self.occ_surface.VDegree()

    @property
    def knots_u(self) -> List[float]:
        return list(self.occ_surface.UKnots())

    @property
    def knots_v(self) -> List[float]:
        return list(self.occ_surface.VKnots())

    @property
    def mults_u(self) -> List[int]:
        return list(self.occ_surface.UMultiplicities())

    @property
    def mults_v(self) -> List[int]:
        return list(self.occ_surface.VMultiplicities())

    # ==============================================================================
    # Methods
    # ==============================================================================

    def copy(self) -> "OCCNurbsSurface":
        """Make an independent copy of the current surface.

        Returns
        -------
        :class:`compas_occ.geometry.OCCNurbsSurface`

        """
        cls = type(self)
        return cls.__from_data__(deepcopy(self.__data__))
