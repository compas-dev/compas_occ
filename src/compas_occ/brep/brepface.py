from typing import List

from OCC.Core.TopoDS import TopoDS_Face
from OCC.Core.TopoDS import topods_Face

from OCC.Core.TopExp import TopExp_Explorer

from OCC.Core.TopAbs import TopAbs_VERTEX
from OCC.Core.TopAbs import TopAbs_EDGE
from OCC.Core.TopAbs import TopAbs_WIRE

from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.GeomAdaptor import GeomAdaptor_Surface

from compas_occ.brep import BRepVertex
from compas_occ.brep import BRepEdge
from compas_occ.brep import BRepLoop


class BRepFace:
    """Class representing a face in the BRep of a geometric shape."""

    def __init__(self, face: TopoDS_Face):
        self._face = None
        self._adaptor = None
        self._surface = None
        self.face = face

    @property
    def face(self) -> TopoDS_Face:
        return self._face

    @face.setter
    def face(self, face) -> None:
        self._face = topods_Face(face)

    @property
    def vertices(self) -> List[BRepVertex]:
        vertices = []
        explorer = TopExp_Explorer(self.shape, TopAbs_VERTEX)
        while explorer.More():
            vertex = explorer.Current()
            vertices.append(BRepVertex(vertex))
            explorer.Next()
        return vertices

    @property
    def edges(self) -> List[BRepEdge]:
        edges = []
        explorer = TopExp_Explorer(self.shape, TopAbs_EDGE)
        while explorer.More():
            edge = explorer.Current()
            edges.append(BRepEdge(edge))
            explorer.Next()
        return edges

    @property
    def loops(self) -> List[BRepLoop]:
        loops = []
        explorer = TopExp_Explorer(self.shape, TopAbs_WIRE)
        while explorer.More():
            wire = explorer.Current()
            loops.append(BRepLoop(wire))
            explorer.Next()
        return loops

    @property
    def adaptor(self) -> BRepAdaptor_Surface:
        if not self._adaptor:
            self._adaptor = BRepAdaptor_Surface(self.face)
        return self._adaptor

    @property
    def surface(self) -> GeomAdaptor_Surface:
        if not self._surface:
            self._surface = self.adaptor.Surface()
        return self._surface
