from __future__ import annotations
from typing import List

from OCC.Core.TopoDS import TopoDS_Edge, topods_Edge

from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_VERTEX

from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
from OCC.Core.GeomAdaptor import GeomAdaptor_Curve

from OCC.Core.TopExp import topexp_FirstVertex
from OCC.Core.TopExp import topexp_LastVertex

import compas.geometry
from compas.geometry import Line
from compas.geometry import Circle
from compas.geometry import Plane

from compas_occ.brep import BRepVertex


class BRepEdge:

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
        return self.curve.GetType()

    @property
    def is_line(self) -> bool:
        return self.type == 0

    @property
    def is_circle(self) -> bool:
        return self.type == 1

    @property
    def is_ellipse(self) -> bool:
        return self.type == 2

    @property
    def is_hyperbola(self) -> bool:
        return self.type == 3

    @property
    def is_parabola(self) -> bool:
        return self.type == 4

    @property
    def is_bezier(self) -> bool:
        return self.type == 5

    @property
    def is_bspline(self) -> bool:
        return self.type == 6

    @property
    def is_other(self) -> bool:
        return self.type == 7

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
        if not self.is_line:
            raise ValueError(f'The underlying geometry is not a line: {self.type}')

        a = self.first_vertex.point
        b = self.last_vertex.point
        return Line(a, b)

    def to_circle(self) -> compas.geometry.Circle:
        if not self.is_circle:
            raise ValueError(f'The underlying geometry is not a circle: {self.type}')

        circle = self.curve.Circle()
        location = circle.Location()
        direction = circle.Axis().Direction()
        radius = circle.Radius()
        point = location.X(), location.Y(), location.Z()
        normal = direction.X(), direction.Y(), direction.Z()
        return Circle(Plane(point, normal), radius)
