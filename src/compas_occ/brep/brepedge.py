from typing import Optional

from OCC.Core import BRepAdaptor
from OCC.Core import BRepAlgo
from OCC.Core import BRepBuilderAPI
from OCC.Core import BRepGProp
from OCC.Core import GeomAbs
from OCC.Core import GProp
from OCC.Core import TopAbs
from OCC.Core import TopExp
from OCC.Core import TopoDS

import compas.geometry
import compas_occ.conversions
from compas.geometry import Bezier
from compas.geometry import BrepEdge
from compas.geometry import Circle
from compas.geometry import Ellipse
from compas.geometry import Hyperbola
from compas.geometry import Line
from compas.geometry import NurbsCurve
from compas.geometry import Parabola
from compas.geometry import Point
from compas_occ.brep import OCCBrepVertex
from compas_occ.conversions import bezier_to_compas
from compas_occ.conversions import bspline_to_compas
from compas_occ.conversions import circle_to_compas
from compas_occ.conversions import circle_to_occ
from compas_occ.conversions import ellipse_to_compas
from compas_occ.conversions import hyperbola_to_compas
from compas_occ.conversions import line_to_occ
from compas_occ.conversions import parabola_to_compas
from compas_occ.conversions import point_to_occ
from compas_occ.geometry import OCCCurve
from compas_occ.geometry import OCCCurve2d
from compas_occ.geometry import OCCSurface


class CurveType:
    LINE = 0
    CIRCLE = 1
    ELLIPSE = 2
    HYPERBOLA = 3
    PARABOLA = 4
    BEZIER = 5
    BSPLINE = 6
    OTHER = 7
    CURVE2D = 8


class OCCBrepEdge(BrepEdge):
    """Class representing an edge in the BRep of a geometric shape.

    Parameters
    ----------
    occ_edge : TopoDS_Edge
        An OCC BRep edge.

    Attributes
    ----------
    curve : :class:`~compas_occ.geometry.OCCCurve`
        Curve geometry from the edge adaptor.
    first_vertex : :class:`~compas_occ.brep.BrepVertex`, read-only
        The first vertex with forward orientation.
    is_line : bool, read-only
        True if the underlying curve is a line.
    is_circle : bool, read-only
        True if the underlying curve is a circle.
    is_ellipse : bool, read-only
        True if the underlying curve is an ellipse.
    is_hyperbola : bool, read-only
        True if the underlying curve is a hyperbola.
    is_parabola : bool, read-only
        True if the underlying curve is a parabola.
    is_bezier : bool, read-only
        True if the underlying curve is a bezier curve.
    is_bspline : bool, read-only
        True if the underlying curve is a bspline curve.
    is_other : bool, read-only
        True if the underlying curve is an other type of curve.
    last_vertex : :class:`~compas_occ.brep.BrepVertex`, read-only
        The first vertex with reversed orientation.
    vertices : list[:class:`~compas_occ.brep.BrepVertex`], read-only
        The topological vertices of the edge.
    type : :class:`BrepEdge.CurveType`, read-only
        The type of the geometric curve underlying the topological edge.

    """

    _occ_edge: TopoDS.TopoDS_Edge

    @property
    def __data__(self) -> dict:
        raise NotImplementedError

    @classmethod
    def __from_data__(cls, data: dict) -> "OCCBrepEdge":
        raise NotImplementedError

    def __init__(self, occ_edge: TopoDS.TopoDS_Edge) -> None:
        super().__init__()
        self._occ_adaptor = None
        self._occ_edge = occ_edge
        self.is_2d = False

    def __eq__(self, other: "OCCBrepEdge") -> bool:
        return self.is_equal(other)

    def is_same(self, other: "OCCBrepEdge") -> bool:
        """Check if this edge is the same as another edge.

        Two edges are the same if they have the same location.

        Parameters
        ----------
        other : :class:`OCCBrepEdge`
            The other edge.

        Returns
        -------
        bool
            ``True`` if the edges are the same, ``False`` otherwise.

        """
        if not isinstance(other, OCCBrepEdge):
            return False
        return self.occ_edge.IsSame(other.occ_edge)

    def is_equal(self, other: "OCCBrepEdge") -> bool:
        """Check if this edge is equal to another edge.

        Two edges are equal if they have the same location and orientation.

        Parameters
        ----------
        other : :class:`OCCBrepEdge`
            The other edge.

        Returns
        -------
        bool
            ``True`` if the edges are equal, ``False`` otherwise.

        """
        if not isinstance(other, OCCBrepEdge):
            return False
        return self.occ_edge.IsEqual(other.occ_edge)

    # ==============================================================================
    # OCC Properties
    # ==============================================================================

    @property
    def occ_shape(self) -> TopoDS.TopoDS_Edge:
        return self.occ_edge

    @property
    def occ_edge(self) -> TopoDS.TopoDS_Edge:
        return self._occ_edge

    @occ_edge.setter
    def occ_edge(self, edge: TopoDS.TopoDS_Edge) -> None:
        self._occ_adaptor = None
        self._curve = None
        self._nurbscurve = None  # remove this if possible
        self._occ_edge = edge

    @property
    def occ_adaptor(self) -> BRepAdaptor.BRepAdaptor_Curve:
        if not self._occ_adaptor:
            self._occ_adaptor = BRepAdaptor.BRepAdaptor_Curve(self.occ_edge)
        return self._occ_adaptor

    @property
    def orientation(self) -> TopAbs.TopAbs_Orientation:
        return self.occ_edge.Orientation()

    @property
    def curve(self) -> compas.geometry.Curve:
        if self.is_curve2d:
            curve2 = self.occ_adaptor.CurveOnSurface().GetCurve()
            ctype2 = curve2.GetType()

            if ctype2 == CurveType.LINE:
                return compas_occ.conversions.line2d_to_compas(curve2.Line())
            if ctype2 == CurveType.CIRCLE:
                return compas_occ.conversions.circle2d_to_compas(curve2.Circle())
            if ctype2 == CurveType.ELLIPSE:
                return compas_occ.conversions.ellipse2d_to_compas(curve2.Ellipse())
            if ctype2 == CurveType.HYPERBOLA:
                return compas_occ.conversions.hyperbola2d_to_compas(curve2.Hyperbola())
            if ctype2 == CurveType.PARABOLA:
                return compas_occ.conversions.parabola2d_to_compas(curve2.Parabola())

        else:
            if self.is_line:
                return self.to_line()
            if self.is_circle:
                return self.to_circle()
            if self.is_ellipse:
                return self.to_ellipse()
            if self.is_hyperbola:
                return self.to_hyperbola()
            if self.is_parabola:
                return self.to_parabola()
            if self.is_bezier:
                return self.to_bezier()
            if self.is_bspline:
                return self.to_bspline()

        raise NotImplementedError

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def type(self) -> int:
        return self.occ_adaptor.GetType()

    @property
    def is_curve2d(self) -> bool:
        return self.type == CurveType.CURVE2D

    @property
    def is_line(self) -> bool:
        return self.type == CurveType.LINE

    @property
    def is_circle(self) -> bool:
        return self.type == CurveType.CIRCLE

    @property
    def is_ellipse(self) -> bool:
        return self.type == CurveType.ELLIPSE

    @property
    def is_hyperbola(self) -> bool:
        return self.type == CurveType.HYPERBOLA

    @property
    def is_parabola(self) -> bool:
        return self.type == CurveType.PARABOLA

    @property
    def is_bezier(self) -> bool:
        return self.type == CurveType.BEZIER

    @property
    def is_bspline(self) -> bool:
        return self.type == CurveType.BSPLINE

    @property
    def is_other(self) -> bool:
        return self.type == CurveType.OTHER

    @property
    def is_valid(self) -> bool:
        return BRepAlgo.brepalgo.IsValid(self.occ_edge)

    @property
    def vertices(self) -> list[OCCBrepVertex]:
        vertices = []
        explorer = TopExp.TopExp_Explorer(self.occ_edge, TopAbs.TopAbs_VERTEX)  # type: ignore
        while explorer.More():
            vertex = explorer.Current()
            vertices.append(OCCBrepVertex(vertex))  # type: ignore
            explorer.Next()
        return vertices

    @property
    def first_vertex(self) -> OCCBrepVertex:
        return OCCBrepVertex(TopExp.topexp.FirstVertex(self.occ_edge))

    @property
    def last_vertex(self) -> OCCBrepVertex:
        return OCCBrepVertex(TopExp.topexp.LastVertex(self.occ_edge))

    @property
    def length(self) -> float:
        props = GProp.GProp_GProps()
        BRepGProp.brepgprop.LinearProperties(self.occ_edge, props)
        return props.Mass()

    @property
    def domain(self) -> tuple[float, float]:
        return self.occ_adaptor.FirstParameter(), self.occ_adaptor.LastParameter()

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_vertex_vertex(cls, a: OCCBrepVertex, b: OCCBrepVertex) -> "OCCBrepEdge":
        """Construct an edge from two vertices.

        Parameters
        ----------
        a : :class:`~compas_occ.brep.BrepVertex`
            The first vertex.
        b : :class:`~compas_occ.brep.BrepVertex`
            The second vertex.

        Returns
        -------
        :class:`~compas_occ.brep.BrepEdge`
            The constructed edge.

        """
        builder = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(a.occ_vertex, b.occ_vertex)
        return cls(builder.Edge())

    @classmethod
    def from_point_point(cls, a: Point, b: Point) -> "OCCBrepEdge":
        """Construct an edge from two points.

        Parameters
        ----------
        a : :class:`compas.geometry.Point`
            The first point.
        b : :class:`compas.geometry.Point`
            The second point.

        Returns
        -------
        :class:`~compas_occ.brep.BrepEdge`
            The constructed edge.

        """
        builder = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(point_to_occ(a), point_to_occ(b))
        return cls(builder.Edge())

    @classmethod
    def from_line(
        cls,
        line: Line,
        params: Optional[tuple[float, float]] = None,
        points: Optional[tuple[Point, Point]] = None,
        vertices: Optional[tuple[OCCBrepVertex, OCCBrepVertex]] = None,
    ) -> "OCCBrepEdge":
        """Construct an edge from a line.

        Parameters
        ----------
        line : :class:`compas.geometry.Line`
            The line.
        params : tuple of float, optional
            The parameters of the line.
        points : tuple of :class:`compas.geometry.Point`, optional
            The start and end points of the line.
        vertices : tuple of :class:`~compas_occ.brep.BrepVertex`, optional
            The start and end vertices of the line.

        Returns
        -------
        :class:`~compas_occ.brep.BrepEdge`
            The constructed edge.

        """
        if params:
            builder = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(line_to_occ(line), *params)
        elif points:
            builder = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(
                line_to_occ(line),
                point_to_occ(points[0]),
                point_to_occ(points[1]),
            )
        elif vertices:
            builder = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(
                line_to_occ(line),
                vertices[0].occ_vertex,
                vertices[1].occ_vertex,
            )
        else:
            builder = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(line_to_occ(line))
        return cls(builder.Edge())

    @classmethod
    def from_circle(
        cls,
        circle: Circle,
        params: Optional[tuple[float, float]] = None,
        points: Optional[tuple[Point, Point]] = None,
        vertices: Optional[tuple[OCCBrepVertex, OCCBrepVertex]] = None,
    ) -> "OCCBrepEdge":
        """Construct an edge from a circle.

        Parameters
        ----------
        circle : :class:`compas.geometry.Circle`
            The circle.
        params : tuple of float, optional
            The parameters of the circle.
        points : tuple of :class:`compas.geometry.Point`, optional
            The start and end points of the circle.
        vertices : tuple of :class:`~compas_occ.brep.BrepVertex`, optional
            The start and end vertices of the circle.

        Returns
        -------
        :class:`~compas_occ.brep.BrepEdge`
            The constructed edge.

        """
        if params:
            builder = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(circle_to_occ(circle), *params)
        elif points:
            builder = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(
                circle_to_occ(circle),
                point_to_occ(points[0]),
                point_to_occ(points[1]),
            )
        elif vertices:
            builder = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(
                circle_to_occ(circle),
                vertices[0].occ_vertex,
                vertices[1].occ_vertex,
            )
        else:
            builder = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(circle_to_occ(circle))
        return cls(builder.Edge())

    @classmethod
    def from_ellipse(cls, ellipse: Ellipse) -> "OCCBrepEdge":
        """Construct an edge from an ellipse.

        Parameters
        ----------
        ellipse : :class:`compas.geometry.Ellipse`
            The ellipse.

        Returns
        -------
        :class:`~compas_occ.brep.BrepEdge`
            The constructed edge.

        """
        raise NotImplementedError

    @classmethod
    def from_curve(
        cls,
        curve: OCCCurve,
        params: Optional[tuple[float, float]] = None,
        points: Optional[tuple[Point, Point]] = None,
        vertices: Optional[tuple[OCCBrepVertex, OCCBrepVertex]] = None,
    ) -> "OCCBrepEdge":
        """Construct an edge from a curve.

        Parameters
        ----------
        curve : :class:`~compas_occ.geometry.OCCCurve`, optional
            The curve.
        params : tuple of float, optional
            The parameters of the curve.
        points : tuple of :class:`compas.geometry.Point`, optional
            The start and end points of the curve.
        vertices : tuple of :class:`~compas_occ.brep.BrepVertex`, optional
            The start and end vertices of the curve.

        Returns
        -------
        :class:`~compas_occ.brep.BrepEdge`
            The constructed edge.

        """
        if points:
            p1 = point_to_occ(points[0])
            p2 = point_to_occ(points[1])
            if params:
                builder = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(curve.occ_curve, p1, p2, *params)
            else:
                builder = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(curve.occ_curve, p1, p2)
        elif vertices:
            v1 = vertices[0].occ_vertex
            v2 = vertices[1].occ_vertex
            if params:
                builder = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(curve.occ_curve, v1, v2, *params)
            else:
                builder = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(curve.occ_curve, v1, v2)
        else:
            if params:
                builder = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(curve.occ_curve, *params)
            else:
                builder = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(curve.occ_curve)

        return cls(builder.Edge())

    @classmethod
    def from_curve_and_surface(
        cls,
        curve: OCCCurve,
        surface: OCCSurface,
        params: Optional[tuple[float, float]] = None,
        points: Optional[tuple[Point, Point]] = None,
        vertices: Optional[tuple[OCCBrepVertex, OCCBrepVertex]] = None,
    ) -> "OCCBrepEdge":
        """Construct an edge from a curve and a surface.

        The curve will be projected onto the surface and embedded into its parameter space automatically.

        Parameters
        ----------
        curve : :class:`~compas_occ.geometry.OCCCurve`
            The curve.
        surface : :class:`~compas_occ.geometry.OCCSurface`
            The surface.
        params : tuple of float, optional
            The parameters of the curve.
        points : tuple of :class:`compas.geometry.Point`, optional
            The start and end points of the curve.
        vertices : tuple of :class:`~compas_occ.brep.BrepVertex`, optional
            The start and end vertices of the curve.

        Returns
        -------
        :class:`~compas_occ.brep.BrepEdge`
            The constructed edge.

        """
        curve2d = curve.projected(surface).embedded(surface)
        return cls.from_curve2d_and_surface(curve2d, surface, params=params, points=points, vertices=vertices)

    @classmethod
    def from_curve2d_and_surface(
        cls,
        curve2d: OCCCurve2d,
        surface: OCCSurface,
        params: Optional[tuple[float, float]] = None,
        points: Optional[tuple[Point, Point]] = None,
        vertices: Optional[tuple[OCCBrepVertex, OCCBrepVertex]] = None,
    ) -> "OCCBrepEdge":
        """Construct an edge from an embedded 2d curve and its embedding surface.

        Parameters
        ----------
        curve2d : :class:`~compas_occ.geometry.OCCCurve2d`
            The 2D curve.
        surface : :class:`~compas_occ.geometry.OCCSurface`
            The surface.
        params : tuple of float, optional
            The parameters of the curve.
        points : tuple of :class:`compas.geometry.Point`, optional
            The start and end points of the curve.
        vertices : tuple of :class:`~compas_occ.brep.BrepVertex`, optional
            The start and end vertices of the curve.

        Returns
        -------
        :class:`~compas_occ.brep.BrepEdge`
            The constructed edge.

        """
        if points:
            p1 = point_to_occ(points[0])
            p2 = point_to_occ(points[1])
            if params:
                builder = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(curve2d.occ_curve, surface.occ_surface, p1, p2, *params)
            else:
                builder = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(curve2d.occ_curve, surface.occ_surface, p1, p2)
        elif vertices:
            v1 = vertices[0].occ_vertex
            v2 = vertices[1].occ_vertex
            if params:
                builder = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(curve2d.occ_curve, surface.occ_surface, v1, v2, *params)
            else:
                builder = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(curve2d.occ_curve, surface.occ_surface, v1, v2)
        else:
            if params:
                builder = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(curve2d.occ_curve, surface.occ_surface, *params)
            else:
                builder = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(curve2d.occ_curve, surface.occ_surface)

        return cls(builder.Edge())

    # ==============================================================================
    # Conversions
    # ==============================================================================

    def to_line(self) -> Line:
        """Convert the edge geometry to a line.

        Returns
        -------
        :class:`~compas.geometry.Line`
            A COMPAS line.

        Raises
        ------
        ValueError
            If the underlying geometry is not a line.

        """
        a = self.first_vertex.point
        b = self.last_vertex.point
        return Line(a, b)

    def to_circle(self) -> Circle:
        """Convert the edge geometry to a circle.

        Returns
        -------
        :class:`~compas.geometry.Circle`
            A COMPAS circle.

        Raises
        ------
        ValueError
            If the underlying geometry is not a circle.

        """
        if not self.is_circle:
            raise ValueError(f"The underlying geometry is not a circle: {self.type}")

        circle = self.occ_adaptor.Circle()
        return circle_to_compas(circle)

    def to_ellipse(self) -> Ellipse:
        """Convert the edge geometry to an ellipse.

        Returns
        -------
        :class:`~compas.geometry.Ellipse`
            A COMPAS ellipse.

        Raises
        ------
        ValueError
            If the underlying geometry is not an ellipse.

        """
        if not self.is_ellipse:
            raise ValueError(f"The underlying geometry is not an ellipse: {self.type}")

        ellipse = self.occ_adaptor.Ellipse()
        return ellipse_to_compas(ellipse)

    def to_hyperbola(self) -> Hyperbola:
        """Convert the edge geometry to a hyperbola.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If the underlying geometry is not a hyperbola.

        """
        if not self.is_hyperbola:
            raise ValueError(f"The underlying geometry is not a hyperbola: {self.type}")

        hyperbola = self.occ_adaptor.Hyperbola()
        return hyperbola_to_compas(hyperbola)

    def to_parabola(self) -> Parabola:
        """Convert the edge geometry to a parabola.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If the underlying geometry is not a parabola.

        """
        if not self.is_parabola:
            raise ValueError(f"The underlying geometry is not a parabola: {self.type}")

        parabola = self.occ_adaptor.Parabola()
        return parabola_to_compas(parabola)

    def to_bezier(self) -> Bezier:
        """Convert the edge geometry to a bezier curve.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If the underlying geometry is not a bezier curve.

        """
        if not self.is_bezier:
            raise ValueError(f"The underlying geometry is not a bezier: {self.type}")

        bezier = self.occ_adaptor.Bezier()
        return bezier_to_compas(bezier)

    def to_bspline(self) -> NurbsCurve:
        """Convert the edge geometry to a bspline.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If the underlying geometry is not a bspline.

        """
        if not self.is_bspline:
            raise ValueError(f"The underlying geometry is not a bspline: {self.type}")

        bspline = self.occ_adaptor.BSpline()
        return bspline_to_compas(bspline)
