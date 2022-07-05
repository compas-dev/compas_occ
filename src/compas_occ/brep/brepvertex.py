from OCC.Core.TopoDS import TopoDS_Vertex
from OCC.Core.TopoDS import topods_Vertex
from OCC.Core.BRep import BRep_Tool_Pnt
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex

from compas.data import Data
from compas.geometry import Point
from compas_occ.conversions.primitives import compas_point_to_occ_point


class BRepVertex(Data):
    """Class representing a vertex in the BRep of a geometric shape.

    Parameters
    ----------
    occ_vertex : ``TopoDS_Vertex``
        An OCC topological vertex data structure.

    Attributes
    ----------
    point : :class:`~compas.geometry.Point`, read-only
        The geometric point underlying the topological vertex.

    Other Attributes
    ----------------
    occ_vertex : ``TopoDS_Vertex``
        The underlying OCC vertex.

    """

    def __init__(self, occ_vertex: TopoDS_Vertex = None):
        super().__init__()
        self._occ_vertex = None
        if occ_vertex:
            self.occ_vertex = occ_vertex

    # ==============================================================================
    # Data
    # ==============================================================================

    @property
    def data(self):
        return {
            "point": self.point.data,
        }

    @data.setter
    def data(self, data):
        point = BRepVertex.from_point(Point.from_data(data["point"]))
        self.occ_vertex = point.occ_vertex

    # ==============================================================================
    # OCC Properties
    # ==============================================================================

    @property
    def occ_vertex(self) -> TopoDS_Vertex:
        return self._occ_vertex

    @occ_vertex.setter
    def occ_vertex(self, vertex) -> None:
        self._occ_vertex = topods_Vertex(vertex)

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def point(self) -> Point:
        p = BRep_Tool_Pnt(self.occ_vertex)
        return Point(p.X(), p.Y(), p.Z())

    @point.setter
    def point(self, point: Point) -> None:
        builder = BRepBuilderAPI_MakeVertex(compas_point_to_occ_point(point))
        self.occ_vertex = builder.Vertex()

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_point(cls, point: Point) -> "BRepVertex":
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
