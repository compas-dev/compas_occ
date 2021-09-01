from typing import List
from enum import Enum

from OCC.Core.TopoDS import TopoDS_Edge, topods_Edge

from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_VERTEX

from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
from OCC.Core.GeomAdaptor import GeomAdaptor_Curve

from OCC.Core.TopExp import topexp_FirstVertex
from OCC.Core.TopExp import topexp_LastVertex

import compas.geometry
from compas.geometry import Line
from compas.geometry import Plane
from compas.geometry import Circle
from compas.geometry import Ellipse

from compas_occ.brep import BRepVertex


class BRepEdge:
    """Class representing an edge in the BRep of a geometric shape.

    Attributes
    ----------
    edge : :class:`TopoDS_Edge`
        The underlying OCC topological edge data structure.
    type : :class:`BRepEdge.CurveType`, read-only
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
    vertices : list of :class:`BRepVertex`, read-only
        The topological vertices of the edge.
    first_vertex : :class:`BRepVertex`, read-only
        The first vertex with forward orientation.
    last_vertex : :class:`BRepVertex`, read-only
        The first vertex with reversed orientation.
    adaptor
    curve
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

    def __init__(self, edge: TopoDS_Edge):
        self._edge = None
        self._adaptor = None
        self._curve = None
        self.edge = edge

    @property
    def edge(self) -> TopoDS_Edge:
        return self._edge

    @edge.setter
    def edge(self, edge: TopoDS_Edge) -> None:
        self._edge = topods_Edge(edge)

    @property
    def type(self) -> int:
        return BRepEdge.CurveType(self.curve.GetType())

    @property
    def is_line(self) -> bool:
        return self.type == BRepEdge.CurveType.Line

    @property
    def is_circle(self) -> bool:
        return self.type == BRepEdge.CurveType.Circle

    @property
    def is_ellipse(self) -> bool:
        return self.type == BRepEdge.CurveType.Ellipse

    @property
    def is_hyperbola(self) -> bool:
        return self.type == BRepEdge.CurveType.Hyperbola

    @property
    def is_parabola(self) -> bool:
        return self.type == BRepEdge.CurveType.Parabola

    @property
    def is_bezier(self) -> bool:
        return self.type == BRepEdge.CurveType.Bezier

    @property
    def is_bspline(self) -> bool:
        return self.type == BRepEdge.CurveType.BSpline

    @property
    def is_other(self) -> bool:
        return self.type == BRepEdge.CurveType.Other

    @property
    def vertices(self) -> List[BRepVertex]:
        vertices = []
        explorer = TopExp_Explorer(self.edge, TopAbs_VERTEX)
        while explorer.More():
            vertex = explorer.Current()
            vertices.append(BRepVertex(vertex))
            explorer.Next()
        return vertices

    @property
    def first_vertex(self) -> BRepVertex:
        return BRepVertex(topexp_FirstVertex(self.edge))

    @property
    def last_vertex(self) -> BRepVertex:
        return BRepVertex(topexp_LastVertex(self.edge))

    @property
    def adaptor(self) -> BRepAdaptor_Curve:
        if not self._adaptor:
            self._adaptor = BRepAdaptor_Curve(self.edge)
        return self._adaptor

    @property
    def curve(self) -> GeomAdaptor_Curve:
        if not self._curve:
            self._curve = self.adaptor.Curve()
        return self._curve

    def to_line(self) -> compas.geometry.Line:
        """Convert the edge geometry to a line.

        Returns
        -------
        :class:`Line`
            A COMPAS line.

        Raises
        ------
        ValueError
            If the underlying geometry is not a line.
        """
        if not self.is_line:
            raise ValueError(f'The underlying geometry is not a line: {self.type}')

        a = self.first_vertex.point
        b = self.last_vertex.point
        return Line(a, b)

    def to_circle(self) -> compas.geometry.Circle:
        """Convert the edge geometry to a circle.

        Returns
        -------
        :class:`Circle`
            A COMPAS circle.

        Raises
        ------
        ValueError
            If the underlying geometry is not a circle.
        """
        if not self.is_circle:
            raise ValueError(f'The underlying geometry is not a circle: {self.type}')

        circle = self.curve.Circle()
        location = circle.Location()
        direction = circle.Axis().Direction()
        radius = circle.Radius()
        point = location.X(), location.Y(), location.Z()
        normal = direction.X(), direction.Y(), direction.Z()
        return Circle(Plane(point, normal), radius)

    def to_ellipse(self) -> compas.geometry.Ellipse:
        """Convert the edge geometry to an ellipse.

        Returns
        -------
        :class:`Ellipse`
            A COMPAS ellipse.

        Raises
        ------
        ValueError
            If the underlying geometry is not an ellipse.
        """
        if not self.is_ellipse:
            raise ValueError(f'The underlying geometry is not an ellipse: {self.type}')

        ellipse = self.curve.Ellipse()
        location = ellipse.Location()
        direction = ellipse.Axis().Direction()
        major = ellipse.MajorRadius()
        minor = ellipse.MinorRadius()
        point = location.X(), location.Y(), location.Z()
        normal = direction.X(), direction.Y(), direction.Z()
        return Ellipse(Plane(point, normal), major, minor)

    def to_hyperbola(self) -> None:
        """Convert the edge geometry to a hyperbola.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If the underlying geometry is not a hyperbola.
        NotImplementedError
            In all other cases
        """
        if not self.is_hyperbola:
            raise ValueError(f'The underlying geometry is not a hyperbola: {self.type}')

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
        NotImplementedError
            In all other cases
        """
        if not self.is_parabola:
            raise ValueError(f'The underlying geometry is not a parabola: {self.type}')

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
        NotImplementedError
            In all other cases
        """
        if not self.is_bezier:
            raise ValueError(f'The underlying geometry is not a bezier: {self.type}')

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
        NotImplementedError
            In all other cases
        """
        if not self.is_bspline:
            raise ValueError(f'The underlying geometry is not a bspline: {self.type}')

        raise NotImplementedError
