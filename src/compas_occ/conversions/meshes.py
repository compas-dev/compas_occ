from typing import Annotated
from typing import List
from typing import Union

import compas.geometry
from compas.datastructures import Mesh
from compas.geometry import Point
from compas.geometry import Polygon
from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from OCC.Core.BRepFill import BRepFill_Filling
from OCC.Core.GeomAbs import GeomAbs_C0
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline
from OCC.Core.GeomFill import geomfill
from OCC.Core.gp import gp_Pnt
from OCC.Core.TopoDS import TopoDS_Face
from OCC.Core.TopoDS import TopoDS_Shell
from OCC.Extend.TopologyUtils import TopologyExplorer

from .arrays import array1_from_points1

Triangle = Union[Polygon, Annotated[List[Union[Annotated[List[float], 3], compas.geometry.Point]], 3]]
Quad = Union[Polygon, Annotated[List[Union[Annotated[List[float], 3], compas.geometry.Point]], 4]]
NGon = Union[Polygon, List[Union[Annotated[List[float], 3], compas.geometry.Point]]]


def triangle_to_face(triangle: Triangle) -> TopoDS_Face:
    """Convert a triangle to a BRep face.

    Parameters
    ----------
    triangle : [point, point, point]
        Three points defining a triangle.

    Returns
    -------
    TopoDS_Face

    Raises
    ------
    ValueError
        If the number of points is not 3.

    See Also
    --------
    :func:`quad_to_face`
    :func:`ngon_to_face`

    Examples
    --------
    >>> triangle = [[0, 0, 0], [1, 0, 0], [0, 1, 0]]
    >>> triangle_to_face(triangle)
    <class 'TopoDS_Face'>

    """
    if len(triangle) != 3:
        raise ValueError("The number of input points should be three.")

    polygon = BRepBuilderAPI_MakePolygon()
    for point in triangle:
        polygon.Add(gp_Pnt(*point))
    polygon.Close()
    wire = polygon.Wire()
    return BRepBuilderAPI_MakeFace(wire).Face()


def quad_to_face(quad: Quad) -> TopoDS_Face:
    """Convert a quad to a BRep face with an underlying ruled surface.

    Parameters
    ----------
    quad : [point, point, point, point]
        Four points defining a quad.

    Returns
    -------
    TopoDS_Face

    Raises
    ------
    ValueError
        If the number of points is not 4.

    See Also
    --------
    :func:`triangle_to_face`
    :func:`ngon_to_face`

    Examples
    --------
    >>> quad = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
    >>> quad_to_face(quad)
    <class 'TopoDS_Face'>

    """
    if len(quad) != 4:
        raise ValueError("The number of input points should be four.")

    points = [Point(*point) for point in quad]
    curve1 = GeomAPI_PointsToBSpline(array1_from_points1([points[0], points[1]])).Curve()
    curve2 = GeomAPI_PointsToBSpline(array1_from_points1([points[3], points[2]])).Curve()
    srf = geomfill.Surface(curve1, curve2)
    return BRepBuilderAPI_MakeFace(srf, 1e-6).Face()


def ngon_to_face(ngon: NGon) -> TopoDS_Face:
    """Convert a Ngon to a BRep face with an underlying best-fit surface.

    Parameters
    ----------
    ngon : sequence[point]
        Points defining a polygon.

    Returns
    -------
    TopoDS_Face

    See Also
    --------
    :func:`triangle_to_face`
    :func:`quad_to_face`

    """
    points = [gp_Pnt(*point) for point in ngon]
    poly = BRepBuilderAPI_MakePolygon()
    for point in points:
        poly.Add(point)
    poly.Build()
    poly.Close()
    edges = TopologyExplorer(poly.Wire()).edges()
    nsided = BRepFill_Filling()
    for edge in edges:
        nsided.Add(edge, GeomAbs_C0)
    nsided.Build()
    return nsided.Face()


def compas_trimesh_to_occ_shell(mesh: Mesh) -> TopoDS_Shell:
    """Convert a COMPAS triangle mesh to an OCC shell.

    Parameters
    ----------
    mesh : :class:`~compas.datastructures.Mesh`
        A COMPAS mesh data structure with triangle faces.

    Returns
    -------
    TopoDS_Shell

    Raises
    ------
    ValueError
        If the mesh is not a triangle mesh.

    See Also
    --------
    :func:`compas_quadmesh_to_occ_shell`
    :func:`compas_mesh_to_occ_shell`

    """
    if not mesh.is_trimesh():
        raise ValueError("The input mesh is not a triangle mesh.")

    shell = TopoDS_Shell()
    builder = BRep_Builder()
    builder.MakeShell(shell)

    for face in mesh.faces():
        points = mesh.face_coordinates(face)
        builder.Add(shell, triangle_to_face(points))  # type: ignore

    return shell


def compas_quadmesh_to_occ_shell(mesh: Mesh) -> TopoDS_Shell:
    """Convert a COMPAS quad mesh to an OCC shell.

    Parameters
    ----------
    mesh : :class:`~compas.datastructures.Mesh`
        A COMPAS mesh data structure with quad faces.

    Returns
    -------
    TopoDS_Shell

    Raises
    ------
    ValueError
        If the input mesh is not a quad mesh.

    See Also
    --------
    :func:`compas_trimesh_to_occ_shell`
    :func:`compas_mesh_to_occ_shell`

    """
    if not mesh.is_quadmesh():
        raise ValueError("The input mesh is not a quad mesh.")

    shell = TopoDS_Shell()
    builder = BRep_Builder()
    builder.MakeShell(shell)

    for face in mesh.faces():
        points = mesh.face_coordinates(face)
        builder.Add(shell, quad_to_face(points))  # type: ignore

    return shell


def compas_mesh_to_occ_shell(mesh: Mesh) -> TopoDS_Shell:
    """Convert a general COMPAS mesh to an OCC shell.

    Parameters
    ----------
    mesh : :class:`~compas.datastructures.Mesh`
        A COMPAS mesh data structure.

    Returns
    -------
    TopoDS_Shell

    See Also
    --------
    :func:`compas_trimesh_to_occ_shell`
    :func:`compas_quadmesh_to_occ_shell`

    """
    shell = TopoDS_Shell()
    builder = BRep_Builder()
    builder.MakeShell(shell)

    for face in mesh.faces():
        points = mesh.face_coordinates(face)

        if len(points) == 3:
            builder.Add(shell, triangle_to_face(points))  # type: ignore
        elif len(points) == 4:
            builder.Add(shell, quad_to_face(points))  # type: ignore
        else:
            builder.Add(shell, ngon_to_face(points))  # type: ignore

    return shell
