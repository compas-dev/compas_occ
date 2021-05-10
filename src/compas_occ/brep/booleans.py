from compas_occ.brep.datastructures import BRepShape
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse


def boolean_union_shape_shape(A, B):
    """Compute the boolean union of two BRep shapes."""
    fuse = BRepAlgoAPI_Fuse(A.to_occ_shape(), B.to_occ_shape())
    if not fuse.IsDone():
        raise Exception("Boolean operation could not be completed.")

    return BRepShape(fuse.Shape())
