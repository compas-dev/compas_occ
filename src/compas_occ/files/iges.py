"""IGES file reading and writing through Open CASCADE."""

from dataclasses import dataclass
from typing import Iterable

from OCC.Core import IFSelect
from OCC.Core import IGESControl

from compas_occ.brep import OCCBrep

from ._geometry import FileGeometry
from ._geometry import FilePath
from ._geometry import shape_from_geometry


@dataclass
class IGESDocument:
    """Collection of geometries stored as separate IGES roots.

    Parameters
    ----------
    geometries
        The geometries in the document.

    """

    geometries: list[FileGeometry]


class IGESReader:
    """Read all root geometries from an IGES file."""

    def __init__(self, source: FilePath) -> None:
        self.source = source

    def read(self) -> IGESDocument:
        """Read the IGES document.

        Returns
        -------
        IGESDocument
            The geometries stored as separate roots.

        """
        reader = IGESControl.IGESControl_Reader()
        status = reader.ReadFile(str(self.source))
        if status != IFSelect.IFSelect_RetDone:
            raise ValueError("The IGES file could not be read: {}".format(self.source))

        geometries = []
        for index in range(1, reader.NbRootsForTransfer() + 1):
            before = reader.NbShapes()
            if not reader.TransferOneRoot(index):
                continue
            for shape_index in range(before + 1, reader.NbShapes() + 1):
                geometries.append(OCCBrep.from_native(reader.Shape(shape_index)))
        return IGESDocument(geometries)


class IGESWriter:
    """Write geometries as separate roots of an IGES file."""

    def __init__(self, target: FilePath) -> None:
        self.target = target

    def write(self, document: IGESDocument, unit: str = "MM", mode: int = 0) -> None:
        """Write an IGES document.

        Parameters
        ----------
        document
            The document to write.
        unit
            Base unit for the geometry.
        mode
            IGES write mode: `0` writes faces and `1` writes BReps.

        """
        if mode not in (0, 1):
            raise ValueError("IGES write mode must be 0 (faces) or 1 (BRep).")
        if not document.geometries:
            raise ValueError("An IGES document requires at least one geometry.")

        writer = IGESControl.IGESControl_Writer(unit, mode)
        for geometry in document.geometries:
            shape = shape_from_geometry(geometry, "IGES")
            if not writer.AddShape(shape):
                raise ValueError("A geometry could not be transferred to the IGES document.")
        writer.ComputeModel()
        if not writer.Write(str(self.target)):
            raise ValueError("The IGES file could not be written: {}".format(self.target))


def read_iges(source: FilePath) -> IGESDocument:
    """Read all geometries from an IGES file."""
    return IGESReader(source).read()


def write_iges(
    target: FilePath,
    geometries: Iterable[FileGeometry],
    unit: str = "MM",
    mode: int = 0,
) -> None:
    """Write multiple geometries to an IGES file."""
    IGESWriter(target).write(IGESDocument(list(geometries)), unit=unit, mode=mode)
