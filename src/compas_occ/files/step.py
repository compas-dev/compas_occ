"""STEP file reading and writing through Open CASCADE."""

from dataclasses import dataclass
from typing import Iterable
from typing import Optional

from OCC.Core import APIHeaderSection
from OCC.Core import IFSelect
from OCC.Core import Interface
from OCC.Core import STEPControl
from OCC.Core import TCollection

from compas_occ.brep import OCCBrep

from ._geometry import FileGeometry
from ._geometry import FilePath
from ._geometry import shape_from_geometry


@dataclass
class STEPDocument:
    """Collection of geometries stored as separate STEP roots.

    Parameters
    ----------
    geometries
        The geometries in the document.

    """

    geometries: list[FileGeometry]


class STEPReader:
    """Read all root geometries from a STEP file."""

    def __init__(self, source: FilePath) -> None:
        self.source = source

    def read(self) -> STEPDocument:
        """Read the STEP document.

        Returns
        -------
        STEPDocument
            The geometries stored as separate STEP roots.

        """
        reader = STEPControl.STEPControl_Reader()
        status = reader.ReadFile(str(self.source))
        if status != IFSelect.IFSelect_RetDone:
            raise ValueError("The STEP file could not be read: {}".format(self.source))

        geometries = []
        for index in range(1, reader.NbRootsForTransfer() + 1):
            before = reader.NbShapes()
            if not reader.TransferRoot(index):
                continue
            for shape_index in range(before + 1, reader.NbShapes() + 1):
                geometries.append(OCCBrep.from_native(reader.Shape(shape_index)))
        return STEPDocument(geometries)


class STEPWriter:
    """Write geometries as separate roots of a STEP file."""

    def __init__(self, target: FilePath) -> None:
        self.target = target

    def write(
        self,
        document: STEPDocument,
        unit: str = "MM",
        author: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        organization: Optional[str] = None,
    ) -> None:
        """Write a STEP document.

        Parameters
        ----------
        document
            The document to write.
        unit
            Base unit for the geometry.
        author
            File author.
        name
            Product name.
        description
            File description.
        organization
            Author organization.

        """
        writer = STEPControl.STEPControl_Writer()
        Interface.Interface_Static.SetCVal("write.step.unit", unit)
        if name:
            Interface.Interface_Static.SetCVal("write.step.product.name", name)

        for geometry in document.geometries:
            shape = shape_from_geometry(geometry, "STEP")
            status = writer.Transfer(shape, STEPControl.STEPControl_StepModelType.STEPControl_AsIs)  # type: ignore[arg-type]
            if status != IFSelect.IFSelect_RetDone:
                raise ValueError("A geometry could not be transferred to the STEP document.")

        if author or description or organization:
            _set_header(writer, author, description, organization)

        status = writer.Write(str(self.target))
        if status != IFSelect.IFSelect_RetDone:
            raise ValueError("The STEP file could not be written: {}".format(self.target))


def read_step(source: FilePath) -> STEPDocument:
    """Read all geometries from a STEP file."""
    return STEPReader(source).read()


def write_step(
    target: FilePath,
    geometries: Iterable[FileGeometry],
    unit: str = "MM",
    author: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    organization: Optional[str] = None,
) -> None:
    """Write multiple geometries to a STEP file."""
    document = STEPDocument(list(geometries))
    STEPWriter(target).write(document, unit, author, name, description, organization)


def _set_header(writer, author, description, organization) -> None:
    model = writer.Model()
    model.ClearHeader()
    header = APIHeaderSection.APIHeaderSection_MakeHeader()
    if author:
        header.SetAuthorValue(1, TCollection.TCollection_HAsciiString(author))
    if organization:
        header.SetOrganizationValue(1, TCollection.TCollection_HAsciiString(organization))
    if description:
        header.SetDescriptionValue(1, TCollection.TCollection_HAsciiString(description))
    model.AddHeaderEntity(header.FnValue())
    model.AddHeaderEntity(header.FsValue())
    model.AddHeaderEntity(header.FdValue())
