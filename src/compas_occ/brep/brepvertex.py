from OCC.Core.TopoDS import TopoDS_Vertex
from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex

from compas.geometry import Point
from compas.brep import BrepVertex
from compas_occ.conversions.geometry import compas_point_to_occ_point


class OCCBrepVertex(BrepVertex):
    """Class representing a vertex in the BRep of a geometric shape.

    Parameters
    ----------
    occ_vertex : ``TopoDS_Vertex``
        An OCC topological vertex data structure.

    Attributes
    ----------
    point : :class:`~compas.geometry.Point`, read-only
        The geometric point underlying the topological vertex.

    """

    def __init__(self, occ_vertex: TopoDS_Vertex):
        super().__init__()
        self._occ_vertex = None
        self.occ_vertex = occ_vertex

    # ==============================================================================
    # Data
    # ==============================================================================

    @property
    def data(self):
        return {
            "point": self.point.data,
        }

    @classmethod
    def from_data(cls, data):
        return cls.from_point(Point.from_data(data["point"]))

    # ==============================================================================
    # OCC Properties
    # ==============================================================================

    @property
    def occ_vertex(self) -> TopoDS_Vertex:
        return self._occ_vertex  # type: ignore

    @occ_vertex.setter
    def occ_vertex(self, occ_vertex: TopoDS_Vertex) -> None:
        self._occ_vertex = occ_vertex

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def point(self) -> Point:
        p = BRep_Tool.Pnt(self.occ_vertex)
        return Point(p.X(), p.Y(), p.Z())

    @point.setter
    def point(self, point: Point) -> None:
        builder = BRepBuilderAPI_MakeVertex(compas_point_to_occ_point(point))
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
        builder = BRepBuilderAPI_MakeVertex(compas_point_to_occ_point(point))
        return cls(builder.Vertex())
