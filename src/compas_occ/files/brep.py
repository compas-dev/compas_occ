"""Open CASCADE BREP file reading and writing."""

from dataclasses import dataclass
from typing import Iterable

from OCC.Core import BRep
from OCC.Core import BRepTools
from OCC.Core import TopAbs
from OCC.Core import TopoDS

from compas_occ.brep import OCCBrep

from ._geometry import FileGeometry
from ._geometry import FilePath
from ._geometry import shape_from_geometry


@dataclass
class BREPDocument:
    """Collection of geometries stored in a native Open CASCADE BREP file.

    Multiple geometries are represented by direct children of a compound.

    Parameters
    ----------
    geometries
        The geometries in the document.

    """

    geometries: list[FileGeometry]


class BREPReader:
    """Read geometries from a native Open CASCADE BREP file."""

    def __init__(self, source: FilePath) -> None:
        self.source = source

    def read(self) -> BREPDocument:
        """Read the BREP document.

        Returns
        -------
        BREPDocument
            The top-level geometries in the document.

        """
        shape = TopoDS.TopoDS_Shape()
        builder = BRep.BRep_Builder()
        if not BRepTools.breptools.Read(shape, str(self.source), builder):
            raise ValueError("The BREP file could not be read: {}".format(self.source))

        shapes = _top_level_shapes(shape)
        return BREPDocument([OCCBrep.from_native(item) for item in shapes])


class BREPWriter:
    """Write geometries to a native Open CASCADE BREP file."""

    def __init__(self, target: FilePath) -> None:
        self.target = target

    def write(self, document: BREPDocument) -> None:
        """Write a BREP document.

        Parameters
        ----------
        document
            The document to write.

        """
        if not document.geometries:
            raise ValueError("A BREP document requires at least one geometry.")

        shapes = [shape_from_geometry(geometry, "BREP") for geometry in document.geometries]
        shape = shapes[0] if len(shapes) == 1 else _compound_from_shapes(shapes)
        if not BRepTools.breptools.Write(shape, str(self.target)):
            raise ValueError("The BREP file could not be written: {}".format(self.target))


def read_brep(source: FilePath) -> BREPDocument:
    """Read all top-level geometries from a BREP file."""
    return BREPReader(source).read()


def write_brep(target: FilePath, geometries: Iterable[FileGeometry]) -> None:
    """Write geometries to a BREP file."""
    BREPWriter(target).write(BREPDocument(list(geometries)))


def _top_level_shapes(shape: TopoDS.TopoDS_Shape) -> list[TopoDS.TopoDS_Shape]:
    if shape.ShapeType() != TopAbs.TopAbs_COMPOUND:
        return [shape]

    shapes = []
    iterator = TopoDS.TopoDS_Iterator(shape)
    while iterator.More():
        shapes.append(iterator.Value())
        iterator.Next()
    return shapes


def _compound_from_shapes(shapes: list[TopoDS.TopoDS_Shape]) -> TopoDS.TopoDS_Compound:
    compound = TopoDS.TopoDS_Compound()
    builder = BRep.BRep_Builder()
    builder.MakeCompound(compound)
    for shape in shapes:
        builder.Add(compound, shape)
    return compound
