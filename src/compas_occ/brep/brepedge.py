from typing import List
from typing import Tuple
from typing import Optional

from enum import Enum

from OCC.Core.TopAbs import TopAbs_VERTEX
from OCC.Core.TopAbs import TopAbs_Orientation
from OCC.Core.TopoDS import TopoDS_Edge
from OCC.Core.TopoDS import topods
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopExp import topexp_FirstVertex
from OCC.Core.TopExp import topexp_LastVertex
from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.BRepAlgo import brepalgo_IsValid
from OCC.Core.BRepGProp import brepgprop_LinearProperties
from OCC.Core.GProp import GProp_GProps

# from OCC.Core.GeomConvert import GeomConvert_ApproxCurve
# from OCC.Core.GeomAbs import GeomAbs_Shape

from compas.geometry import Point
from compas.geometry import Line
from compas.geometry import Circle
from compas.geometry import Ellipse
from compas.brep import BrepEdge

from compas_occ.brep import OCCBrepVertex

from compas_occ.conversions import compas_line_to_occ_line
from compas_occ.conversions import compas_point_to_occ_point
from compas_occ.conversions import compas_circle_to_occ_circle

from compas_occ.conversions import compas_circle_from_occ_circle
from compas_occ.conversions import compas_ellipse_from_occ_ellipse

from compas_occ.geometry import OCCCurve
from compas_occ.geometry import OCCCurve2d
from compas_occ.geometry import OCCNurbsCurve
from compas_occ.geometry import OCCSurface


class OCCBrepEdge(BrepEdge):
    """Class representing an edge in the BRep of a geometric shape.

    Parameters
    ----------
    occ_edge : TopoDS_Edge
        An OCC BRep edge.

    Attributes
    ----------
    type : :class:`BrepEdge.CurveType`, read-only
        The type of the geometric curve underlying the topological edge.
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
    vertices : list[:class:`~compas_occ.brep.BrepVertex`], read-only
        The topological vertices of the edge.
    first_vertex : :class:`~compas_occ.brep.BrepVertex`, read-only
        The first vertex with forward orientation.
    last_vertex : :class:`~compas_occ.brep.BrepVertex`, read-only
        The first vertex with reversed orientation.
    curve : :class:`~compas_occ.geometry.OCCCurve`
        Curve geometry from the edge adaptor.

    Other Attributes
    ----------------
    occ_edge : ``TopoDS_Edge``
        The underlying OCC topological edge data structure.
    occ_adaptor : ``BRepAdaptor_Curve``
        Edge adaptor for extracting curve geometry.

    """

    class CurveType(Enum):
        Line = 0
        Circle = 1
        Ellipse = 2
        Hyperbola = 3
        Parabola = 4
        Bezier = 5
        BSpline = 6
        Other = 7
        Curve2D = 8

    def __init__(self, occ_edge: TopoDS_Edge):
        super().__init__()
        self._curve = None
        self._nurbscurve = None
        self._occ_edge = None
        self._occ_adaptor = None
        self.occ_edge = occ_edge

    # ==============================================================================
    # Data
    # ==============================================================================

    @property
    def data(self):
        raise NotImplementedError

    @classmethod
    def from_data(cls, data):
        raise NotImplementedError

    # ==============================================================================
    # OCC Properties
    # ==============================================================================

    @property
    def occ_shape(self) -> TopoDS_Edge:
        return self._occ_edge  # type: ignore

    @property
    def occ_edge(self) -> TopoDS_Edge:
        return self._occ_edge  # type: ignore

    @occ_edge.setter
    def occ_edge(self, edge: TopoDS_Edge) -> None:
        self._occ_adaptor = None
        self._curve = None
        self._nurbscurve = None
        self._occ_edge = topods.Edge(edge)

    @property
    def occ_adaptor(self) -> BRepAdaptor_Curve:
        if not self._occ_adaptor:
            self._occ_adaptor = BRepAdaptor_Curve(self.occ_edge)
        return self._occ_adaptor

    @property
    def orientation(self) -> TopAbs_Orientation:
        return self.occ_edge.Orientation()

    @property
    def curve(self) -> OCCCurve:
        if not self._curve:
            occ_curve = self.occ_adaptor.Curve()
            self._curve = OCCCurve(occ_curve)  # type: ignore
        return self._curve

    @property
    def nurbscurve(self) -> OCCNurbsCurve:
        if not self._nurbscurve:
            occ_curve = self.occ_adaptor.BSpline()
            self._nurbscurve = OCCNurbsCurve(occ_curve)  # type: ignore
        return self._nurbscurve  # type: ignore (don't understand why this is necessary)

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def type(self) -> int:
        return OCCBrepEdge.CurveType(self.occ_adaptor.GetType())  # type: ignore

    @property
    def is_curve2d(self) -> bool:
        return self.type == OCCBrepEdge.CurveType.Curve2D

    @property
    def is_line(self) -> bool:
        return self.type == OCCBrepEdge.CurveType.Line

    @property
    def is_circle(self) -> bool:
        return self.type == OCCBrepEdge.CurveType.Circle

    @property
    def is_ellipse(self) -> bool:
        return self.type == OCCBrepEdge.CurveType.Ellipse

    @property
    def is_hyperbola(self) -> bool:
        return self.type == OCCBrepEdge.CurveType.Hyperbola

    @property
    def is_parabola(self) -> bool:
        return self.type == OCCBrepEdge.CurveType.Parabola

    @property
    def is_bezier(self) -> bool:
        return self.type == OCCBrepEdge.CurveType.Bezier

    @property
    def is_bspline(self) -> bool:
        return self.type == OCCBrepEdge.CurveType.BSpline

    @property
    def is_other(self) -> bool:
        return self.type == OCCBrepEdge.CurveType.Other

    @property
    def is_valid(self) -> bool:
        return brepalgo_IsValid(self.occ_edge)

    @property
    def vertices(self) -> List[OCCBrepVertex]:
        vertices = []
        explorer = TopExp_Explorer(self.occ_edge, TopAbs_VERTEX)
        while explorer.More():
            vertex = explorer.Current()
            vertices.append(OCCBrepVertex(vertex))  # type: ignore
            explorer.Next()
        return vertices

    @property
    def first_vertex(self) -> OCCBrepVertex:
        return OCCBrepVertex(topexp_FirstVertex(self.occ_edge))

    @property
    def last_vertex(self) -> OCCBrepVertex:
        return OCCBrepVertex(topexp_LastVertex(self.occ_edge))

    @property
    def length(self) -> float:
        props = GProp_GProps()
        brepgprop_LinearProperties(self.occ_edge, props)
        return props.Mass()

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_vertex_vertex(cls, a: OCCBrepVertex, b: OCCBrepVertex) -> "OCCBrepEdge":
        """Construct an edge from two vertices."""
        builder = BRepBuilderAPI_MakeEdge(a.occ_vertex, b.occ_vertex)
        return cls(builder.Edge())

    @classmethod
    def from_point_point(cls, a: Point, b: Point) -> "OCCBrepEdge":
        """Construct an edge from two points."""
        builder = BRepBuilderAPI_MakeEdge(
            compas_point_to_occ_point(a), compas_point_to_occ_point(b)
        )
        return cls(builder.Edge())

    @classmethod
    def from_line(
        cls,
        line: Line,
        params: Optional[Tuple[float, float]] = None,
        points: Optional[Tuple[Point, Point]] = None,
        vertices: Optional[Tuple[OCCBrepVertex, OCCBrepVertex]] = None,
    ) -> "OCCBrepEdge":
        """Construct an edge from a line."""
        if params:
            builder = BRepBuilderAPI_MakeEdge(compas_line_to_occ_line(line), *params)
        elif points:
            builder = BRepBuilderAPI_MakeEdge(
                compas_line_to_occ_line(line),
                compas_point_to_occ_point(points[0]),
                compas_point_to_occ_point(points[1]),
            )
        elif vertices:
            builder = BRepBuilderAPI_MakeEdge(
                compas_line_to_occ_line(line),
                vertices[0].occ_vertex,
                vertices[1].occ_vertex,
            )
        else:
            builder = BRepBuilderAPI_MakeEdge(compas_line_to_occ_line(line))
        return cls(builder.Edge())

    @classmethod
    def from_circle(
        cls,
        circle: Circle,
        params: Optional[Tuple[float, float]] = None,
        points: Optional[Tuple[Point, Point]] = None,
        vertices: Optional[Tuple[OCCBrepVertex, OCCBrepVertex]] = None,
    ) -> "OCCBrepEdge":
        """Construct an edge from a circle."""
        if params:
            builder = BRepBuilderAPI_MakeEdge(
                compas_circle_to_occ_circle(circle), *params
            )
        elif points:
            builder = BRepBuilderAPI_MakeEdge(
                compas_circle_to_occ_circle(circle),
                compas_point_to_occ_point(points[0]),
                compas_point_to_occ_point(points[1]),
            )
        elif vertices:
            builder = BRepBuilderAPI_MakeEdge(
                compas_circle_to_occ_circle(circle),
                vertices[0].occ_vertex,
                vertices[1].occ_vertex,
            )
        else:
            builder = BRepBuilderAPI_MakeEdge(compas_circle_to_occ_circle(circle))
        return cls(builder.Edge())

    @classmethod
    def from_ellipse(cls, ellipse: Ellipse) -> "OCCBrepEdge":
        raise NotImplementedError

    @classmethod
    def from_curve(
        cls,
        curve: Optional[OCCCurve] = None,
        curve2d: Optional[OCCCurve2d] = None,
        surface: Optional[OCCSurface] = None,
        params: Optional[Tuple[float, float]] = None,
        points: Optional[Tuple[Point, Point]] = None,
        vertices: Optional[Tuple[OCCBrepVertex, OCCBrepVertex]] = None,
    ) -> "OCCBrepEdge":
        """Construct an edge from a curve."""

        if curve and curve2d:
            raise ValueError("Providing both a 2D and a 3D curve is not possible.")

        if not curve and not curve2d:
            raise ValueError("Not providing any input curve is not possible.")

        if surface:
            if curve:
                curve2d = curve.projected(surface).embedded(surface)

            if not curve2d:
                raise ValueError("No curve was provided.")

            if points:
                p1 = compas_point_to_occ_point(points[0])
                p2 = compas_point_to_occ_point(points[1])
                if params:
                    builder = BRepBuilderAPI_MakeEdge(
                        curve2d.occ_curve, surface.occ_surface, p1, p2, *params
                    )
                else:
                    builder = BRepBuilderAPI_MakeEdge(
                        curve2d.occ_curve, surface.occ_surface, p1, p2
                    )
            elif vertices:
                v1 = vertices[0].occ_vertex
                v2 = vertices[1].occ_vertex
                if params:
                    builder = BRepBuilderAPI_MakeEdge(
                        curve2d.occ_curve, surface.occ_surface, v1, v2, *params
                    )
                else:
                    builder = BRepBuilderAPI_MakeEdge(
                        curve2d.occ_curve, surface.occ_surface, v1, v2
                    )
            else:
                if params:
                    builder = BRepBuilderAPI_MakeEdge(
                        curve2d.occ_curve, surface.occ_surface, *params
                    )
                else:
                    builder = BRepBuilderAPI_MakeEdge(
                        curve2d.occ_curve, surface.occ_surface
                    )
        else:
            if not curve:
                raise ValueError("No curve was provided.")

            if points:
                p1 = compas_point_to_occ_point(points[0])
                p2 = compas_point_to_occ_point(points[1])
                if params:
                    builder = BRepBuilderAPI_MakeEdge(curve.occ_curve, p1, p2, *params)
                else:
                    builder = BRepBuilderAPI_MakeEdge(curve.occ_curve, p1, p2)
            elif vertices:
                v1 = vertices[0].occ_vertex
                v2 = vertices[1].occ_vertex
                if params:
                    builder = BRepBuilderAPI_MakeEdge(curve.occ_curve, v1, v2, *params)
                else:
                    builder = BRepBuilderAPI_MakeEdge(curve.occ_curve, v1, v2)
            else:
                if params:
                    builder = BRepBuilderAPI_MakeEdge(curve.occ_curve, *params)
                else:
                    builder = BRepBuilderAPI_MakeEdge(curve.occ_curve)

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
        if not self.is_line:
            raise ValueError(f"The underlying geometry is not a line: {self.type}")

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

        curve = self.occ_adaptor.Curve()
        circle = curve.Circle()
        return compas_circle_from_occ_circle(circle)

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

        curve = self.occ_adaptor.Curve()
        ellipse = curve.Ellipse()
        return compas_ellipse_from_occ_ellipse(ellipse)

    def to_hyperbola(self) -> None:
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
        raise NotImplementedError

    def to_parabola(self) -> None:
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
        raise NotImplementedError

    def to_bezier(self) -> None:
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
        raise NotImplementedError

    def to_bspline(self) -> None:
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
        raise NotImplementedError

    def to_curve(self) -> OCCCurve:
        """Convert the edge geometry to a NURBS curve.

        Returns
        -------
        :class:`~compas_occ.geometry.OCCCurve`

        """
        return self.curve

    # ==============================================================================
    # Methods
    # ==============================================================================

    # def try_get_nurbscurve(
    #     self,
    #     precision=1e-3,
    #     continuity=None,
    #     maxsegments=1,
    #     maxdegree=5,
    # ) -> OCCNurbsCurve:
    #     """Try to convert the underlying geometry to a Nurbs curve."""
    #     nurbs = OCCNurbsCurve()
    #     try:
    #         occ_curve = self.occ_adaptor.BSpline()
    #     except Exception as e:
    #         print(e)
    #         convert = GeomConvert_ApproxCurve(
    #             self.occ_adaptor,
    #             precision,
    #             GeomAbs_Shape.GeomAbs_C1,
    #             maxsegments,
    #             maxdegree,
    #         )  # type: ignore
    #         occ_curve = convert.Curve()
    #     nurbs.occ_curve = occ_curve
    #     return nurbs
