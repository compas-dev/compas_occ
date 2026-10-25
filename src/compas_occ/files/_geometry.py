"""Shared geometry types for CAD exchange files."""

from os import PathLike
from typing import Protocol
from typing import Union

from OCC.Core.TopoDS import TopoDS_Shape

FilePath = Union[str, PathLike[str]]


class OCCShapeProvider(Protocol):
    @property
    def occ_shape(self) -> TopoDS_Shape: ...


class NativeBrepProvider(Protocol):
    @property
    def native_brep(self) -> TopoDS_Shape: ...


FileGeometry = Union[TopoDS_Shape, OCCShapeProvider, NativeBrepProvider]


def shape_from_geometry(geometry: FileGeometry, format_name: str) -> TopoDS_Shape:
    """Extract an OCC shape from exchange geometry."""
    if isinstance(geometry, TopoDS_Shape):
        return geometry
    shape = getattr(geometry, "occ_shape", None)
    if shape is None:
        shape = getattr(geometry, "native_brep", None)
    if not isinstance(shape, TopoDS_Shape):
        raise TypeError("{} geometry must be a TopoDS_Shape or expose one through occ_shape or native_brep.".format(format_name))
    return shape
