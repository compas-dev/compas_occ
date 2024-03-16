from compas.geometry import BrepVertex
from compas.geometry import Point
from OCC.Core import BRep
from OCC.Core import BRepBuilderAPI
from OCC.Core import TopoDS

from compas_occ.conversions.geometry import point_to_occ


class OCCBrepVertex(BrepVertex):
    """Class representing a vertex in the BRep of a geometric shape.

    Parameters
    ----------
    occ_vertex : ``TopoDS.TopoDS_Vertex``
        An OCC topological vertex data structure.

    Attributes
    ----------
    point : :class:`~compas.geometry.Point`, read-only
        The geometric point underlying the topological vertex.

    """

    @property
    def __data__(self):
        return {
            "point": self.point.__data__,
        }

    @classmethod
    def __from_data__(cls, data):
        return cls.from_point(Point.__from_data__(data["point"]))

    def __init__(self, occ_vertex: TopoDS.TopoDS_Vertex):
        super().__init__()
        self._occ_vertex = None
        self.occ_vertex = occ_vertex

    def __eq__(self, other: "OCCBrepVertex"):
        return self.is_equal(other)

    def is_same(self, other: "OCCBrepVertex"):
        """Check if this vertex is the same as another vertex.

        Two vertices are the same if they have the same location.

        Parameters
        ----------
        other : :class:`OCCBrepVertex`
            The other vertex.

        Returns
        -------
        bool
            ``True`` if the vertices are the same, ``False`` otherwise.

        """
        if not isinstance(other, OCCBrepVertex):
            return False
        return self.occ_vertex.IsSame(other.occ_vertex)

    def is_equal(self, other: "OCCBrepVertex"):
        """Check if this vertex is equal to another vertex.

        Two vertices are equal if they have the same location and orientation.

        Parameters
        ----------
        other : :class:`OCCBrepVertex`
            The other vertex.

        Returns
        -------
        bool
            ``True`` if the vertices are equal, ``False`` otherwise.

        """
        if not isinstance(other, OCCBrepVertex):
            return False
        return self.occ_vertex.IsEqual(other.occ_vertex)

    # ==============================================================================
    # OCC Properties
    # ==============================================================================

    @property
    def occ_vertex(self) -> TopoDS.TopoDS_Vertex:
        return self._occ_vertex  # type: ignore

    @occ_vertex.setter
    def occ_vertex(self, occ_vertex: TopoDS.TopoDS_Vertex) -> None:
        self._occ_vertex = occ_vertex

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def point(self) -> Point:
        p = BRep.BRep_Tool.Pnt(self.occ_vertex)
        return Point(p.X(), p.Y(), p.Z())

    @point.setter
    def point(self, point: Point) -> None:
        builder = BRepBuilderAPI.BRepBuilderAPI_MakeVertex(point_to_occ(point))
        self._occ_vertex = builder.Vertex()

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_point(cls, point: Point) -> "BrepVertex":
        """Construct a vertex from a point.

        Parameters
        ----------
        point : :class:`compas.geometry.Point`
            The point.

        Returns
        -------
        :class:`BrepVertex`

        """
        builder = BRepBuilderAPI.BRepBuilderAPI_MakeVertex(point_to_occ(point))
        return cls(builder.Vertex())
