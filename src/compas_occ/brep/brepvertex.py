from OCC.Core.TopoDS import TopoDS_Vertex
from OCC.Core.TopoDS import topods_Vertex

from OCC.Core.BRep import BRep_Tool_Pnt

import compas.geometry
from compas.geometry import Point


class BRepVertex:
    """Class representing a vertex in the BRep of a geometric shape.

    Attributes
    ----------
    vertex : :class:`TopoDS_Vertex`
        The underlying OCC vertex.
    point : :class:`Point`, read-only
        The geometric point underlying the topological vertex.

    Parameters
    ----------
    vertex : :class:`TopoDS_Vertex`
        An OCC topological vertex data structure.
    """

    def __init__(self, vertex: TopoDS_Vertex):
        self._vertex = None
        self.vertex = vertex

    @property
    def vertex(self):
        return self._vertex

    @vertex.setter
    def vertex(self, vertex) -> None:
        self._vertex = topods_Vertex(vertex)

    @property
    def point(self) -> compas.geometry.Point:
        p = BRep_Tool_Pnt(self.vertex)
        return Point(p.X(), p.Y(), p.Z())
