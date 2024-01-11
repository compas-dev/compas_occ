from OCC.Core.BRep import BRep_Builder
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.TopoDS import TopoDS_Shell

# from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace


TOLERANCE = 1e-6


class OCCBrepBuilder(object):
    """Reconstructs a Rhino.Geometry.Brep from COMPAS types

    Attributes
    ----------
    result : :rhino:`Rhino.Geometry.Brep`
        The Brep resulting from the reconstruction, if successful.

    """

    def __init__(self):
        self.shell = TopoDS_Shell()
        self.builder = BRep_Builder()
        self.builder.MakeShell(self.shell)

    @property
    def result(self) -> TopoDS_Shape:
        return self.shell

    def add_vertex(self, point):
        """Add vertext to a new Brep

        point : :class:`compas.geometry.Point`

        Returns
        -------
        :rhino:`Rhino.Geometry.BrepVertex`

        """
        return self._brep.Vertices.Add(point_to_rhino(point), TOLERANCE)  # noqa: F821

    def add_edge(self, edge_curve, start_vertex, end_vertex):
        """Add edge to the new Brep

        edge_curve : :class:`compas_rhino.geometry.RhinoNurbsCurve`
        start_vertex: int
            index of the vertex at the start of this edge
        end_vertex: int
            index of the vertex at the end of this edge

        Returns
        -------
        :rhino:`Rhino.Geometry.BrepEdge`

        """
        curve_index = self._brep.AddEdgeCurve(edge_curve)
        s_vertex = self._brep.Vertices[start_vertex]
        e_vertex = self._brep.Vertices[end_vertex]
        return self._brep.Edges.Add(s_vertex, e_vertex, curve_index, TOLERANCE)

    def add_face(self, surface):
        """Creates and adds a new face to the brep.

        Returns a new builder to be used by all the loops related to his new face to add themselves.

        Parameters
        ----------
        surface : :rhino:`Rhino.Geometry.Surface`
            The surface of this face.

        Returns
        -------
        :class:`compas_rhino.geometry.RhinoFaceBuilder`

        """
        surface_index = self._brep.AddSurface(surface.rhino_surface)
        face = self._brep.Faces.Add(surface_index)
        return OCCFaceBuilder(face=face, brep=self._brep)  # noqa: F821
