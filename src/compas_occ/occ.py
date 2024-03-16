from compas.geometry import Point
from OCC.Core.BOPAlgo import BOPAlgo_Splitter
from OCC.Core.BRepGProp import brepgprop_VolumeProperties
from OCC.Core.GProp import GProp_GProps
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Core.TopoDS import TopoDS_Iterator
from OCC.Core.TopoDS import TopoDS_Shape

from .conversions import point_to_compas

# =============================================================================
# Brep ops
# =============================================================================


def split_shapes(arguments: list[TopoDS_Shape], tools: list[TopoDS_Shape]) -> list[TopoDS_Shape]:
    """Split a group of breps by another group of breps.

    Parameters
    ----------
    arguments : list[TopoDS_Shape]
        The arguments passed to the command.
    tools : list[TopoDS_Shape]
        The tools passed to the command.

    Returns
    -------
    list[TopoDS_Shape]
        The resulting breps.

    """
    splitter = BOPAlgo_Splitter()

    for occ_shape in arguments:
        splitter.AddArgument(occ_shape)
    for occ_shape in tools:
        splitter.AddTool(occ_shape)

    splitter.Perform()
    shape = splitter.Shape()

    results = []

    if isinstance(shape, TopoDS_Compound):
        it = TopoDS_Iterator(shape)
        while it.More():
            results.append(it.Value())
            it.Next()
    else:
        results.append(shape)

    return results


# =============================================================================
# Brep props
# =============================================================================


def compute_shape_centreofmass(occ_shape: TopoDS_Shape) -> Point:
    """Return a COMPAS Point at the centre of mass of a Brep.

    Parameters
    ----------
    occ_shape : TopoDS_Shape
        The brep.

    Returns
    -------
    :class:`Point`
        The centroid.

    """
    props = GProp_GProps()
    brepgprop_VolumeProperties(occ_shape, props)
    pnt = props.CentreOfMass()
    return point_to_compas(pnt)
