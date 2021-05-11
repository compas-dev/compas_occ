from __future__ import annotations

from typing import List

from compas.datastructures import Mesh

from OCC.Core.TopoDS import (
    TopoDS_Shape,
    TopoDS_Vertex,
    TopoDS_Edge,
    TopoDS_Face,
    TopoDS_Shell,
    TopoDS_Solid
)
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.Interface import Interface_Static_SetCVal
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.Tesselator import ShapeTesselator
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert

from OCC.Extend.TopologyUtils import TopologyExplorer  # noqa F401


# class BRepVertex:
#     pass


# class BRepEdge:
#     pass


# class BRepWire:
#     pass


# class BRepFace:
#     pass


class BRepShape:
    """Wrapper for TopoDS_Shape."""

    def __init__(self, shape: TopoDS_Shape):
        self._occ_shape = None
        self._explorer = None
        self.occ_shape = shape

    @property
    def occ_shape(self):
        return self._occ_shape

    @occ_shape.setter
    def occ_shape(self, occ_shape):
        self._occ_shape = occ_shape
        self._explorer = TopologyExplorer(self._occ_shape)

    @property
    def explorer(self):
        return self._explorer

    def to_step(self, filepath: str, schema: str = "AP203") -> None:
        """Write the shape contained in this wrapper to a STEP file."""
        step_writer = STEPControl_Writer()
        Interface_Static_SetCVal("write.step.schema", schema)
        step_writer.Transfer(self.occ_shape, STEPControl_AsIs)
        status = step_writer.Write(filepath)
        if status != IFSelect_RetDone:
            raise AssertionError("load failed")

    def to_tesselation(self) -> Mesh:
        """Convert the shape contained in this wrapper to a triangulated mesh for visualization."""
        tess = ShapeTesselator(self.occ_shape)
        tess.Compute()
        vertices = [tess.GetVertex(i) for i in range(tess.ObjGetVertexCount())]
        triangles = [tess.GetTriangleIndex(i) for i in range(tess.ObjGetTriangleCount())]
        return Mesh.from_vertices_and_faces(vertices, triangles)

    def to_vizmesh(self) -> Mesh:
        """Convert the shape contained in this wrapper to a clean UV mesh for visualization."""
        pass

    def convert(self) -> None:
        """Convert the shape to a new shape such that the underlying geometry is bspline."""
        converter = BRepBuilderAPI_NurbsConvert(self.occ_shape, False)
        self.occ_shape = converter.Shape()

    def converted(self) -> BRepShape:
        """Convert the shape to a new shape such that the underlying geometry is bspline."""
        converter = BRepBuilderAPI_NurbsConvert(self.occ_shape, True)
        return BRepShape(converter.Shape())

    def vertices(self) -> List[TopoDS_Vertex]:
        return self.explorer.vertices()

    def edges(self) -> List[TopoDS_Edge]:
        return self.explorer.edges()

    def faces(self) -> List[TopoDS_Face]:
        return self.explorer.faces()

    def shells(self) -> List[TopoDS_Shell]:
        return self.explorer.shells()

    def solids(self) -> List[TopoDS_Solid]:
        return self.explorer.solids()
