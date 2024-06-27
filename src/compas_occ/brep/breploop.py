from typing import List

from compas.geometry import BrepLoop
from compas.geometry import Polygon
from compas.geometry import Polyline
from compas.itertools import pairwise
from OCC.Core import BRepAlgo
from OCC.Core import BRepBuilderAPI
from OCC.Core import BRepTools
from OCC.Core import ShapeFix
from OCC.Core import TopoDS

from compas_occ.brep import OCCBrepEdge
from compas_occ.brep import OCCBrepVertex


def wire_from_edges(edges: List[OCCBrepEdge]) -> TopoDS.TopoDS_Wire:
    """Construct a wire from a list of edges.

    Parameters
    ----------
    edges : list[:class:`compas_occ.brep.OCCBrepEdge`]
        The edges.

    Returns
    -------
    ``TopoDS.TopoDS_Wire``

    """
    builder = BRepBuilderAPI.BRepBuilderAPI_MakeWire()
    for edge in edges:
        builder.Add(edge.occ_edge)
    return builder.Wire()


class OCCBrepLoop(BrepLoop):
    """Class representing an edge loop in the BRep of a geometric shape.

    Parameters
    ----------
    occ_wire : ``TopoDS.TopoDS_Wire``
        An OCC BRep wire.

    Attributes
    ----------
    vertices : list[:class:`~compas_occ.brep.BrepVertex`], read-only
        List of BRep vertices.
    edges : list[:class:`~compas_occ.brep.BrepEdge`], read-only
        List of BRep edges.

    """

    _occ_wire: TopoDS.TopoDS_Wire

    @property
    def __data__(self):
        # return {
        #     "type": str(self._loop.LoopType),
        #     "trims": [t.data for t in self._trims],
        # }
        raise NotImplementedError

    @classmethod
    def __from_data__(cls, data, builder):
        """Construct an object of this type from the provided data.

        Parameters
        ----------
        data : dict
            The data dictionary.
        builder : :class:`compas_rhino.geometry.BrepFaceBuilder`
            The object reconstructing the current BrepFace.

        Returns
        -------
        :class:`compas.data.Data`
            An instance of this object type if the data contained in the dict has the correct schema.

        """
        raise NotImplementedError

    def __init__(self, occ_wire: TopoDS.TopoDS_Wire):
        super().__init__()
        self.occ_wire = occ_wire

    def __eq__(self, other: "OCCBrepLoop"):
        return self.is_equal(other)

    def is_same(self, other: "OCCBrepLoop"):
        """Check if this loop is the same as another loop.

        Two loops are the same if they have the same location.

        Parameters
        ----------
        other : :class:`OCCBrepLoop`
            The other loop.

        Returns
        -------
        bool
            ``True`` if the loops are the same, ``False`` otherwise.

        """
        if not isinstance(other, OCCBrepLoop):
            return False
        return self.occ_wire.IsSame(other.occ_wire)

    def is_equal(self, other: "OCCBrepLoop"):
        """Check if this loop is equal to another loop.

        Two loops are equal if they have the same location and orientation.

        Parameters
        ----------
        other : :class:`OCCBrepLoop`
            The other loop.

        Returns
        -------
        bool
            ``True`` if the loops are equal, ``False`` otherwise.

        """
        if not isinstance(other, OCCBrepLoop):
            return False
        return self.occ_wire.IsEqual(other.occ_wire)

    # ==============================================================================
    # OCC Properties
    # ==============================================================================

    @property
    def occ_shape(self) -> TopoDS.TopoDS_Wire:
        return self.occ_wire

    @property
    def occ_wire(self) -> TopoDS.TopoDS_Wire:
        return self._occ_wire

    @occ_wire.setter
    def occ_wire(self, loop: TopoDS.TopoDS_Wire) -> None:
        self._occ_wire = loop

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def is_valid(self) -> bool:
        return BRepAlgo.brepalgo.IsValid(self.occ_wire)

    @property
    def vertices(self) -> List[OCCBrepVertex]:
        vertices = []
        explorer = BRepTools.BRepTools_WireExplorer(self.occ_wire)
        while explorer.More():
            vertex = explorer.CurrentVertex()
            vertices.append(OCCBrepVertex(vertex))
            explorer.Next()
        return vertices

    @property
    def edges(self) -> List[OCCBrepEdge]:
        edges = []
        explorer = BRepTools.BRepTools_WireExplorer(self.occ_wire)
        while explorer.More():
            edge = explorer.Current()
            edges.append(OCCBrepEdge(edge))
            explorer.Next()
        return edges

    @edges.setter
    def edges(self, edges: List[OCCBrepEdge]) -> None:
        self.occ_wire = wire_from_edges(edges)

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_edges(cls, edges: List[OCCBrepEdge]) -> "OCCBrepLoop":
        """Construct a loop from a collection of edges.

        Parameters
        ----------
        edges : list[:class:`compas_occ.brep.BrepEdge`]
            The edges.

        Returns
        -------
        ``OCCBrepLoop``

        """
        return cls(wire_from_edges(edges))

    @classmethod
    def from_polyline(cls, polyline: Polyline) -> "OCCBrepLoop":
        """Construct a loop from a polyline.

        Parameters
        ----------
        polyline : :class:`compas.geometry.Polyline`
            The polyline.

        Returns
        -------
        ``OCCBrepLoop``

        """
        edges = []
        for a, b in pairwise(polyline.points):
            edge = OCCBrepEdge.from_point_point(a, b)
            edges.append(edge)
        return cls(wire_from_edges(edges))

    @classmethod
    def from_polygon(cls, polygon: Polygon) -> "OCCBrepLoop":
        """Construct a loop from a polygon.

        Parameters
        ----------
        polygon : :class:`compas.geometry.Polygon`
            The polygon.

        Returns
        -------
        ``OCCBrepLoop``

        """
        edges = []
        for a, b in pairwise(polygon.points):
            edge = OCCBrepEdge.from_point_point(a, b)
            edges.append(edge)
        return cls(wire_from_edges(edges))

    # ==============================================================================
    # Methods
    # ==============================================================================

    def fix(self) -> None:
        """Try to fix the loop.

        Returns
        -------
        None

        """
        fixer = ShapeFix.ShapeFix_Wire(self.occ_wire)  # type: ignore
        fixer.Perform()
        self.occ_wire = fixer.Wire()
