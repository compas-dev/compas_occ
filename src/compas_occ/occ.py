from OCC.Core import TopAbs
from OCC.Core import TopExp
from OCC.Core import TopoDS
from OCC.Core.BOPAlgo import BOPAlgo_Splitter
from OCC.Core.BRepGProp import brepgprop
from OCC.Core.GProp import GProp_GProps
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Core.TopoDS import TopoDS_Iterator

from compas.geometry import Point

from .conversions import point_to_compas


def split_shapes(arguments: list[TopoDS.TopoDS_Shape], tools: list[TopoDS.TopoDS_Shape]) -> list[TopoDS.TopoDS_Shape]:
    """Split a group of breps by another group of breps.

    Parameters
    ----------
    arguments : list[TopoDS.TopoDS_Shape]
        The arguments passed to the command.
    tools : list[TopoDS.TopoDS_Shape]
        The tools passed to the command.

    Returns
    -------
    list[TopoDS.TopoDS_Shape]
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


def compute_shape_centreofmass(occ_shape: TopoDS.TopoDS_Shape) -> Point:
    """Return a COMPAS Point at the centre of mass of a Brep.

    Parameters
    ----------
    occ_shape : TopoDS.TopoDS_Shape
        The brep.

    Returns
    -------
    :class:`Point`
        The centroid.

    """
    props = GProp_GProps()
    brepgprop.VolumeProperties(occ_shape, props)
    pnt = props.CentreOfMass()
    return point_to_compas(pnt)


def occ_shape_find_vertices(occ_shape: TopoDS.TopoDS_Shape) -> list[TopoDS.TopoDS_Vertex]:
    """Find all the vertices in an OCC shape.

    Parameters
    ----------
    occ_shape : TopoDS.TopoDS_Shape
        The shape to explore.

    Returns
    -------
    list[TopoDS.TopoDS_Vertex]

    """
    vertices: list[TopoDS.TopoDS_Vertex] = []
    explorer = TopExp.TopExp_Explorer(occ_shape, TopAbs.TopAbs_VERTEX)  # type: ignore
    while explorer.More():
        vertex = explorer.Current()
        vertices.append(vertex)  # type: ignore
        explorer.Next()
    return vertices


def occ_shape_find_edges(occ_shape: TopoDS.TopoDS_Shape) -> list[TopoDS.TopoDS_Edge]:
    """Find all the edges in an OCC shape.

    Parameters
    ----------
    occ_shape : TopoDS.TopoDS_Shape
        The shape to explore.

    Returns
    -------
    list[TopoDS.TopoDS_Edge]

    """
    edges: list[TopoDS.TopoDS_Edge] = []
    explorer = TopExp.TopExp_Explorer(occ_shape, TopAbs.TopAbs_EDGE)  # type: ignore
    while explorer.More():
        edge = explorer.Current()
        edges.append(edge)  # type: ignore
        explorer.Next()
    return edges


def occ_shape_find_loops(occ_shape: TopoDS.TopoDS_Shape) -> list[TopoDS.TopoDS_Wire]:
    """Find all the loops or wires in an OCC shape.

    Parameters
    ----------
    occ_shape : TopoDS.TopoDS_Shape
        The shape to explore.

    Returns
    -------
    list[TopoDS.TopoDS_Wire]

    """
    wires: list[TopoDS.TopoDS_Wire] = []
    explorer = TopExp.TopExp_Explorer(occ_shape, TopAbs.TopAbs_WIRE)  # type: ignore
    while explorer.More():
        wire = explorer.Current()
        wires.append(wire)  # type: ignore
        explorer.Next()
    return wires


def occ_shape_find_faces(occ_shape: TopoDS.TopoDS_Shape) -> list[TopoDS.TopoDS_Face]:
    """Find all the faces in an OCC shape.

    Parameters
    ----------
    occ_shape : TopoDS.TopoDS_Shape
        The shape to explore.

    Returns
    -------
    list[TopoDS.TopoDS_Face]

    """
    faces: list[TopoDS.TopoDS_Face] = []
    explorer = TopExp.TopExp_Explorer(occ_shape, TopAbs.TopAbs_FACE)  # type: ignore
    while explorer.More():
        face = explorer.Current()
        faces.append(face)  # type: ignore
        explorer.Next()
    return faces


def occ_shape_find_shells(occ_shape: TopoDS.TopoDS_Shape) -> list[TopoDS.TopoDS_Shell]:
    """Find all the shells in an OCC shape.

    Parameters
    ----------
    occ_shape : TopoDS.TopoDS_Shape
        The shape to explore.

    Returns
    -------
    list[TopoDS.TopoDS_Shell]

    """
    shells: list[TopoDS.TopoDS_Shell] = []
    explorer = TopExp.TopExp_Explorer(occ_shape, TopAbs.TopAbs_SHELL)  # type: ignore
    while explorer.More():
        shell = explorer.Current()
        shells.append(shell)  # type: ignore
        explorer.Next()
    return shells


def occ_shape_find_solids(occ_shape: TopoDS.TopoDS_Shape) -> list[TopoDS.TopoDS_Solid]:
    """Find all the solids in an OCC shape.

    Parameters
    ----------
    occ_shape : TopoDS.TopoDS_Shape
        The shape to explore.

    Returns
    -------
    list[TopoDS.TopoDS_Solid]

    """
    solids: list[TopoDS.TopoDS_Solid] = []
    explorer = TopExp.TopExp_Explorer(occ_shape, TopAbs.TopAbs_SOLID)  # type: ignore
    while explorer.More():
        solid = explorer.Current()
        solids.append(solid)  # type: ignore
        explorer.Next()
    return solids
