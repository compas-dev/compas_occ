from OCC.Core.TopoDS import TopoDS_Vertex
from OCC.Core.TopoDS import topods_Vertex

from OCC.Core.BRep import BRep_Tool_Pnt
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex

import compas.geometry
from compas.geometry import Point

from compas_occ.conversions.primitives import compas_point_to_occ_point


class BRepVertex:
    """Class representing a vertex in the BRep of a geometric shape.

    Parameters
    ----------
    vertex : ``TopoDS_Vertex``
        An OCC topological vertex data structure.

    Attributes
    ----------
    vertex : ``TopoDS_Vertex``
        The underlying OCC vertex.
    point : :class:`~compas.geometry.Point`, read-only
        The geometric point underlying the topological vertex.

    Other Attributes
    ----------------
    vertex : ``TopoDS_Vertex``
        The underlying OCC vertex.

    """

    def __init__(self, vertex: TopoDS_Vertex):
        self._vertex = None
        self.vertex = vertex

    @property
    def vertex(self) -> TopoDS_Vertex:
        return self._vertex

    @vertex.setter
    def vertex(self, vertex) -> None:
        self._vertex = topods_Vertex(vertex)

    @property
    def point(self) -> compas.geometry.Point:
        p = BRep_Tool_Pnt(self.vertex)
        return Point(p.X(), p.Y(), p.Z())

    @classmethod
    def from_point(cls, point: compas.geometry.Point) -> "BRepVertex":
        """Construct a vertex from a point.

        Parameters
        ----------
        point : :class:`compas.geometry.Point`
            The point.

        Returns
        -------
        :class:`BRepVertex`

        """
        builder = BRepBuilderAPI_MakeVertex(compas_point_to_occ_point(point))
        return cls(builder.Vertex())
