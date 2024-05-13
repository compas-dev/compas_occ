from copy import deepcopy
from math import sqrt
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from compas.geometry import Circle
from compas.geometry import Ellipse
from compas.geometry import Frame
from compas.geometry import Line
from compas.geometry import NurbsCurve
from compas.geometry import Point

# from OCC.Core.TopoDS import TopoDS_Edge
from OCC.Core.Geom import Geom_BSplineCurve
from OCC.Core.GeomAPI import GeomAPI_Interpolate
from OCC.Core.GeomConvert import GeomConvert_CompCurveToBSplineCurve
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.TColStd import TColStd_Array1OfInteger
from OCC.Core.TColStd import TColStd_Array1OfReal

from compas_occ.conversions import array1_from_floats1
from compas_occ.conversions import array1_from_integers1
from compas_occ.conversions import array1_from_points1
from compas_occ.conversions import harray1_from_points1
from compas_occ.conversions import point_to_compas
from compas_occ.conversions import points1_from_array1

from .curve import OCCCurve


def occ_curve_from_parameters(
    points: List[Point],
    weights: List[float],
    knots: List[float],
    multiplicities: List[int],
    degree: int,
    is_periodic: bool,
) -> Geom_BSplineCurve:
    return Geom_BSplineCurve(
        array1_from_points1(points),
        array1_from_floats1(weights),
        array1_from_floats1(knots),
        array1_from_integers1(multiplicities),
        degree,
        is_periodic,
    )


class OCCNurbsCurve(OCCCurve, NurbsCurve):
    """Class representing a NURBS curve based on the BSplineCurve of the OCC geometry kernel.

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
    is_rational : bool, read-only
        Flag indicating that the curve is rational.
    knots : list[float], read-only
        The knots of the curve, without multiplicities.
    knotsequence : list[float], read-only
        The full vector of knots of the curve.
    multiplicities : list[int], read-only
        The multiplicities of the knots of the curve.
    order : int, read-only
        The order of the curve (= degree + 1).
    points : list[:class:`~compas.geometry.Point`], read-only
        The control points of the curve.
    weights : list[float], read-only
        The weights of the control points of the curve.

    Examples
    --------
    Curve from points...

    >>> from compas.geometry import Point
    >>> from compas_occ.geometry import OCCNurbsCurve
    >>> points = [Point(0, 0, 0), Point(3, 6, 0), Point(6, -3, 3), Point(10, 0, 0)]
    >>> curve = OCCNurbsCurve.from_points(points)

    Curve from parameters...

    >>> from compas.geometry import Point
    >>> from compas_occ.geometry import OCCNurbsCurve
    >>> points = [Point(0, 0, 0), Point(3, 6, 0), Point(6, -3, 3), Point(10, 0, 0)]
    >>> curve = OCCNurbsCurve.from_parameters(points=points, weights=[1.0, 1.0, 1.0, 1.0], knots=[0.0, 1.0], multiplicities=[4, 4], degree=3)

    """

    _occ_curve: Geom_BSplineCurve

    @property
    def __data__(self) -> Dict:
        return {
            "points": [point.__data__ for point in self.points],
            "weights": self.weights,
            "knots": self.knots,
            "multiplicities": self.multiplicities,
            "degree": self.degree,
            "is_periodic": self.is_periodic,
        }

    @classmethod
    def __from_data__(cls, data: Dict) -> "OCCNurbsCurve":
        points = [Point.__from_data__(point) for point in data["points"]]
        weights = data["weights"]
        knots = data["knots"]
        multiplicities = data["multiplicities"]
        degree = data["degree"]
        is_periodic = data["is_periodic"]
        return cls.from_parameters(
            points,
            weights,
            knots,
            multiplicities,
            degree,
            is_periodic,
        )

    def __init__(self, occ_curve: Geom_BSplineCurve, name: Optional[str] = None):
        super(OCCNurbsCurve, self).__init__(occ_curve, name=name)
        self.occ_curve = occ_curve

    # ==============================================================================
    # OCC Properties
    # ==============================================================================

    @property
    def occ_curve(self) -> Geom_BSplineCurve:
        return self._occ_curve

    @occ_curve.setter
    def occ_curve(self, occ_curve: Geom_BSplineCurve):
        self._occ_curve = occ_curve

    @property
    def occ_points(self) -> TColgp_Array1OfPnt:
        return self.occ_curve.Poles()

    @property
    def occ_weights(self) -> TColStd_Array1OfReal:
        weights = self.occ_curve.Weights()
        if weights:
            return weights
        return array1_from_floats1([1.0] * len(self.occ_points))

    @property
    def occ_knots(self) -> TColStd_Array1OfReal:
        return self.occ_curve.Knots()

    @property
    def occ_knotsequence(self) -> TColStd_Array1OfReal:
        return self.occ_curve.KnotSequence()

    @property
    def occ_multiplicities(self) -> TColStd_Array1OfInteger:
        return self.occ_curve.Multiplicities()

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def start(self) -> Point:
        pnt = self.occ_curve.StartPoint()
        return point_to_compas(pnt)

    @property
    def end(self) -> Point:
        pnt = self.occ_curve.EndPoint()
        return point_to_compas(pnt)

    @property
    def points(self) -> List[Point]:
        return points1_from_array1(self.occ_points)

    @property
    def weights(self) -> List[float]:
        return list(self.occ_weights)

    @property
    def knots(self) -> List[float]:
        return list(self.occ_knots)

    @property
    def knotsequence(self) -> List[float]:
        return list(self.occ_knotsequence)

    @property
    def multiplicities(self) -> List[int]:
        return list(self.occ_multiplicities)

    @property
    def continuity(self) -> int:
        return self.occ_curve.Continuity()

    @property
    def degree(self) -> int:
        return self.occ_curve.Degree()

    @property
    def order(self) -> int:
        return self.degree + 1

    @property
    def is_rational(self) -> bool:
        return self.occ_curve.IsRational()

    # ==============================================================================
    # Constructors
    # ==============================================================================

    # @classmethod
    # def from_edge(cls, edge: TopoDS_Edge) -> Union["OCCNurbsCurve", None]:
    #     """Construct a NURBS curve from an existing OCC TopoDS_Edge.

    #     Parameters
    #     ----------
    #     edge : TopoDS_Edge
    #         The OCC edge containing the curve information.

    #     Returns
    #     -------
    #     :class:`OCCNurbsCurve`

    #     """
    #     from compas_occ.brep import OCCBrepEdge

    #     brepedge = OCCBrepEdge(edge)
    #     if brepedge.is_line:
    #         line = brepedge.to_line()
    #         return cls.from_line(line)

    @classmethod
    def from_parameters(
        cls,
        points: List[Point],
        weights: List[float],
        knots: List[float],
        multiplicities: List[int],
        degree: int,
        is_periodic: bool = False,
    ) -> "OCCNurbsCurve":
        """Construct a NURBS curve from explicit curve parameters.

        Parameters
        ----------
        points : list[:class:`~compas.geometry.Point`]
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
        :class:`OCCNurbsCurve`

        """
        occ_curve = occ_curve_from_parameters(
            points,
            weights,
            knots,
            multiplicities,
            degree,
            is_periodic,
        )
        return cls(occ_curve)

    @classmethod
    def from_points(cls, points: List[Point], degree: int = 3) -> "OCCNurbsCurve":
        """Construct a NURBS curve from control points.

        Parameters
        ----------
        points : list[:class:`~compas.geometry.Point`]
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
        occ_curve = occ_curve_from_parameters(
            points,
            weights,
            knots,
            multiplicities,
            degree,
            is_periodic,
        )
        return cls(occ_curve)

    @classmethod
    def from_interpolation(
        cls,
        points: List[Point],
        precision: float = 1e-3,
    ) -> "OCCNurbsCurve":
        """Construct a NURBS curve by interpolating a set of points.

        Parameters
        ----------
        points : list[:class:`~compas.geometry.Point`]
            The control points of the curve.
        precision : float, optional
            The precision of the interpolation.

        Returns
        -------
        :class:`OCCNurbsCurve`

        """
        # use GeomAPI_PointsToBSpline instead?
        interp = GeomAPI_Interpolate(harray1_from_points1(points), False, precision)
        interp.Perform()
        occ_curve = interp.Curve()
        return cls(occ_curve)

    @classmethod
    def from_arc(cls, arc, degree, pointcount=None) -> "OCCNurbsCurve":
        """Construct a NURBS curve from an arc.

        Parameters
        ----------
        arc : :class:`~compas.geometry.Arc`
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
    def from_circle(cls, circle: Circle) -> "OCCNurbsCurve":
        """Construct a NURBS curve from a circle.

        Parameters
        ----------
        circle : :class:`~compas.geometry.Circle`
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
            frame.point - dy,
        ]
        knots = [0, 1 / 4, 1 / 2, 3 / 4, 1]
        mults = [3, 2, 2, 2, 3]
        weights = [1, w, 1, w, 1, w, 1, w, 1]
        return cls.from_parameters(
            points=points,
            weights=weights,
            knots=knots,
            multiplicities=mults,
            degree=2,
        )

    @classmethod
    def from_ellipse(cls, ellipse: Ellipse) -> "OCCNurbsCurve":
        """Construct a NURBS curve from an ellipse.

        Parameters
        ----------
        ellipse : :class:`~compas.geometry.Ellipse`
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
            frame.point - dy,
        ]
        knots = [0, 1 / 4, 1 / 2, 3 / 4, 1]
        mults = [3, 2, 2, 2, 3]
        weights = [1, w, 1, w, 1, w, 1, w, 1]
        return cls.from_parameters(
            points=points,
            weights=weights,
            knots=knots,
            multiplicities=mults,
            degree=2,
        )

    @classmethod
    def from_line(cls, line: Line) -> "OCCNurbsCurve":
        """Construct a NURBS curve from a line.

        Parameters
        ----------
        line : :class:`~compas.geometry.Line`
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
            degree=1,
        )

    # ==============================================================================
    # Conversions
    # ==============================================================================

    # ==============================================================================
    # Methods
    # ==============================================================================

    def copy(self) -> "OCCNurbsCurve":
        """Make an independent copy of the current curve.

        Returns
        -------
        :class:`compas_occ.geometry.OCCNurbsCurve`

        """
        cls = type(self)
        return cls.__from_data__(deepcopy(self.__data__))

    def segment(self, u: float, v: float, precision: float = 1e-3) -> None:
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
            raise ValueError("At least one of the given parameters is outside the curve domain.")
        if u == v:
            raise ValueError("The given domain is zero length.")
        self.occ_curve.Segment(u, v, precision)

    def segmented(self, u: float, v: float, precision: float = 1e-3) -> "OCCNurbsCurve":
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
        :class:`OCCNurbsCurve`

        """
        copy = self.copy()
        copy.segment(u, v, precision)
        return copy

    def join(self, curve: "OCCNurbsCurve", precision: float = 1e-4) -> None:
        """Modifies this curve by joining it with another curve.

        Parameters
        ----------
        curve : :class:`OCCNurbsCurve`
            The curve to join.
        precision : float, optional
            Tolerance for continuity and multiplicity.

        Returns
        -------
        None

        """
        converter = GeomConvert_CompCurveToBSplineCurve(self.occ_curve)
        success = converter.Add(curve.occ_curve, precision)
        if success:
            self.occ_curve = converter.BSplineCurve()

    def joined(
        self,
        curve: "OCCNurbsCurve",
        precision: float = 1e-4,
    ) -> Union["OCCNurbsCurve", None]:
        """Returns a new curve that is the result of joining this curve with another.

        Parameters
        ----------
        curve : :class:`OCCNurbsCurve`
            The curve to join.
        precision : float, optional
            Tolerance for continuity and multiplicity.

        Returns
        -------
        :class:`OCCNurbsCurve` | None

        """
        copy = self.copy()
        converter = GeomConvert_CompCurveToBSplineCurve(self.occ_curve)
        success = converter.Add(curve.occ_curve, precision)
        if success:
            copy.occ_curve = converter.BSplineCurve()
            return copy
