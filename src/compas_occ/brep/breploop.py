from typing import List

from OCC.Core.TopoDS import TopoDS_Wire
from OCC.Core.TopoDS import topods_Wire
from OCC.Core.BRepTools import BRepTools_WireExplorer
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeWire
from OCC.Core.BRepAlgo import brepalgo_IsValid
from OCC.Core.ShapeFix import ShapeFix_Wire

from compas.data import Data
from compas.utilities import pairwise

from compas.geometry import Polyline
from compas.geometry import Polygon

from compas_occ.brep import BRepVertex
from compas_occ.brep import BRepEdge


class BRepLoop(Data):
    """Class representing an edge loop in the BRep of a geometric shape.

    Parameters
    ----------
    occ_wire : ``TopoDS_Wire``
        An OCC BRep wire.

    Attributes
    ----------
    vertices : list[:class:`~compas_occ.brep.BRepVertex`], read-only
        List of BRep vertices.
    edges : list[:class:`~compas_occ.brep.BRepEdge`], read-only
        List of BRep edges.

    Other Attributes
    ----------------
    occ_wire : ``TopoDS_Wire``
        The OCC BRep wire.

    """

    def __init__(self, occ_wire: TopoDS_Wire = None):
        super().__init__()
        self._occ_wire = None
        if occ_wire:
            self.occ_wire = occ_wire

    # ==============================================================================
    # Data
    # ==============================================================================

    @property
    def data(self):
        edges = []
        for edge in self.edges:
            edges.append(edge.data)
        return edges

    @data.setter
    def data(self, data):
        edges = []
        for edgedata in data:
            edges.append(BRepEdge.from_data(edgedata))
        loop = BRepLoop.from_edges(edges)
        self.occ_wire = loop.occ_wire

    # ==============================================================================
    # OCC Properties
    # ==============================================================================

    @property
    def occ_shape(self):
        return self._occ_wire

    @property
    def occ_wire(self):
        return self._occ_wire

    @occ_wire.setter
    def occ_wire(self, loop: TopoDS_Wire):
        self._occ_wire = topods_Wire(loop)

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def is_valid(self) -> bool:
        return brepalgo_IsValid(self.occ_wire)

    @property
    def vertices(self) -> List[BRepVertex]:
        vertices = []
        explorer = BRepTools_WireExplorer(self.occ_wire)
        while explorer.More():
            vertex = explorer.CurrentVertex()
            vertices.append(BRepVertex(vertex))
            explorer.Next()
        return vertices

    @property
    def edges(self) -> List[BRepEdge]:
        edges = []
        explorer = BRepTools_WireExplorer(self.occ_wire)
        while explorer.More():
            edge = explorer.Current()
            edges.append(BRepEdge(edge))
            explorer.Next()
        return edges

    @edges.setter
    def edges(self, edges: List[BRepEdge]) -> None:
        builder = BRepBuilderAPI_MakeWire()
        for edge in edges:
            builder.Add(edge.occ_edge)
        self.occ_wire = builder.Wire()

    # ==============================================================================
    # Constructors
    # ==============================================================================

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
        loop = cls()
        loop.edges = edges
        return loop

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
        loop = cls()
        loop.edges = edges
        return loop

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
        loop = cls()
        loop.edges = edges
        return loop

    # ==============================================================================
    # Methods
    # ==============================================================================

    def fix(self) -> None:
        """Try to fix the loop.

        Returns
        -------
        None

        """
        fixer = ShapeFix_Wire(self.occ_wire)
        fixer.Perform()
        self.occ_wire = fixer.Wire()
