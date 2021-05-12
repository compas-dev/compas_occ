from __future__ import annotations

from compas_occ.brep.datastructures import BRepShape

from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Common
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse


def boolean_union_shape_shape(A: BRepShape, B: BRepShape, convert: bool = True) -> BRepShape:
    """Compute the boolean union of two BRep shapes."""
    fuse = BRepAlgoAPI_Fuse(A.to_occ_shape(), B.to_occ_shape())
    if not fuse.IsDone():
        raise Exception("Boolean union operation could not be completed.")

    shape = BRepShape(fuse.Shape())
    if convert:
        shape.convert()

    return shape


def boolean_difference_shape_shape(A: BRepShape, B: BRepShape, convert: bool = True) -> BRepShape:
    """Compute the boolean difference between two BRep shapes."""
    cut = BRepAlgoAPI_Cut(A.to_occ_shape(), B.to_occ_shape())
    if not cut.IsDone():
        raise Exception("Boolean difference operation could not be completed.")

    shape = BRepShape(cut.Shape())
    if convert:
        shape.convert()

    return shape


def boolean_intersection_shape_shape(A: BRepShape, B: BRepShape, convert: bool = True) -> BRepShape:
    """Compute the boolean intersection between two BRep shapes."""
    cut = BRepAlgoAPI_Common(A.to_occ_shape(), B.to_occ_shape())
    if not cut.IsDone():
        raise Exception("Boolean intersection operation could not be completed.")

    shape = BRepShape(cut.Shape())
    if convert:
        shape.convert()

    return shape
