from typing import List

from OCC.Core.TopoDS import TopoDS_Wire, topods_Wire

from OCC.Core.BRepTools import BRepTools_WireExplorer

from compas_occ.brep import BRepVertex
from compas_occ.brep import BRepEdge


class BRepLoop:
    """Class representing an edge loop in the BRep of a geometric shape."""

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
