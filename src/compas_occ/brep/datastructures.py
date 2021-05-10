from compas.datastructures import Mesh

from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.Interface import Interface_Static_SetCVal
from OCC.Core.IFSelect import IFSelect_RetDone

from OCC.Core.Tesselator import ShapeTesselator

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
        self.occ_shape = shape

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
