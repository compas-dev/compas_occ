from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.Interface import Interface_Static_SetCVal
from OCC.Core.IFSelect import IFSelect_RetDone


# class BRepVertex:
#     pass


# class BRepEdge:
#     pass


# class BRepWire:
#     pass


# class BRepFace:
#     pass


class BRepShape:

    def __init__(self, shape: TopoDS_Shape):
        self._shape = shape

    def to_step(self, filepath: str, schema: str = "AP203") -> None:
        step_writer = STEPControl_Writer()
        Interface_Static_SetCVal("write.step.schema", schema)
        step_writer.Transfer(self._shape, STEPControl_AsIs)
        status = step_writer.Write(filepath)
        if status != IFSelect_RetDone:
            raise AssertionError("load failed")
