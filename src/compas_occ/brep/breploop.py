from typing import List

from OCC.Core.TopoDS import TopoDS_Wire
from OCC.Core.TopoDS import topods_Wire
from OCC.Core.BRepTools import BRepTools_WireExplorer
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeWire
from OCC.Core.BRepAlgo import brepalgo_IsValid
from OCC.Core.ShapeFix import ShapeFix_Wire

from compas.utilities import pairwise
from compas.geometry import Polyline
from compas.geometry import Polygon

from compas_occ.brep import BRepVertex
from compas_occ.brep import BRepEdge


class BRepLoop:
    """Class representing an edge loop in the BRep of a geometric shape.

    Parameters
    ----------
    loop : ``TopoDS_Wire``
        An OCC BRep wire.

    Attributes
    ----------
    vertices : list[:class:`~compas_occ.brep.BRepVertex`], read-only
        List of BRep vertices.
    edges : list[:class:`~compas_occ.brep.BRepEdge`], read-only
        List of BRep edges.

    Other Attributes
    ----------------
    loop : ``TopoDS_Wire``
        The OCC BRep wire.

    """

    def __init__(self, loop: TopoDS_Wire):
        self._loop = None
        self.loop = loop

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, loop: TopoDS_Wire):
        self._loop = topods_Wire(loop)

    @property
    def vertices(self) -> List[BRepVertex]:
        vertices = []
        explorer = BRepTools_WireExplorer(self.loop)
        while explorer.More():
            vertex = explorer.CurrentVertex()
            vertices.append(BRepVertex(vertex))
            explorer.Next()
        return vertices

    @property
    def edges(self) -> List[BRepEdge]:
        edges = []
        explorer = BRepTools_WireExplorer(self.loop)
        while explorer.More():
            edge = explorer.Current()
            edges.append(BRepEdge(edge))
            explorer.Next()
        return edges

    @classmethod
    def from_edges(cls, edges: List[BRepEdge]) -> "BRepLoop":
        """Construct a loop from a collection of edges.

        Parameters
        ----------
        edges : list[:class:`compas_occ.brep.BRepEdge`]
            The edges.

        Returns
        -------
        ``BRepLoop``

        """
        builder = BRepBuilderAPI_MakeWire()
        for edge in edges:
            builder.Add(edge.edge)
        return cls(builder.Wire())

    @classmethod
    def from_polyline(cls, polyline: Polyline) -> "BRepLoop":
        """Construct a loop from a polyline.

        Parameters
        ----------
        polyline : :class:`compas.geometry.Polyline`
            The polyline.

        Returns
        -------
        ``BRepLoop``

        """
        edges = []
        for a, b in pairwise(polyline.points):
            edge = BRepEdge.from_point_point(a, b)
            edges.append(edge)
        return cls.from_edges(edges)

    @classmethod
    def from_polygon(cls, polygon: Polygon) -> "BRepLoop":
        """Construct a loop from a polygon.

        Parameters
        ----------
        polygon : :class:`compas.geometry.Polygon`
            The polygon.

        Returns
        -------
        ``BRepLoop``

        """
        edges = []
        for a, b in pairwise(polygon.points):
            edge = BRepEdge.from_point_point(a, b)
            edges.append(edge)
        return cls.from_edges(edges)

    def is_valid(self) -> bool:
        """Verify that the loop is valid.

        Returns
        -------
        bool

        """
        return brepalgo_IsValid(self.loop)

    def fix(self) -> None:
        """Try to fix the loop.

        Returns
        -------
        None

        """
        fixer = ShapeFix_Wire(self.loop)
        fixer.Perform()
        self.loop = fixer.Wire()
