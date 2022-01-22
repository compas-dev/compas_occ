from typing import List
from typing import Union
from typing_extensions import Annotated

import compas.geometry
from compas.geometry import Point
from compas.datastructures import Mesh

from .arrays import array1_from_points1

from OCC.Core.gp import gp_Pnt
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline
from OCC.Core.TopoDS import TopoDS_Shell
from OCC.Core.TopoDS import TopoDS_Face
from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Core.GeomFill import geomfill_Surface
from OCC.Core.BRepFill import BRepFill_Filling
from OCC.Core.GeomAbs import GeomAbs_C0
from OCC.Extend.TopologyUtils import TopologyExplorer


Triangle = Annotated[List[Union[Annotated[List[float], 3], compas.geometry.Point]], 3]
Quad = Annotated[List[Union[Annotated[List[float], 3], compas.geometry.Point]], 4]
NGon = List[Union[Annotated[List[float], 3], compas.geometry.Point]]


def triangle_to_face(points: Triangle) -> TopoDS_Face:
    """Convert a triangle to a BRep face.

    Parameters
    ----------
    points : [point, point, point]
        Three points defining a triangle.

    Returns
    -------
    TopoDS_Face

    Raises
    ------
    AssertionError
        If the number of points is not 3.

    """
    assert len(points) == 3, "The number of input points should be three."

    polygon = BRepBuilderAPI_MakePolygon()
    for point in points:
        polygon.Add(gp_Pnt(* point))
    polygon.Close()
    wire = polygon.Wire()
    return BRepBuilderAPI_MakeFace(wire).Face()


def quad_to_face(points: Quad) -> TopoDS_Face:
    """Convert a quad to a BRep face with an underlying ruled surface.

    Parameters
    ----------
    points : [point, point, point, point]
        Four points defining a quad.

    Returns
    -------
    TopoDS_Face

    Raises
    ------
    AssertionError
        If the number of points is not 4.

    """
    assert len(points) == 4, "The number of input points should be four."

    points = [Point(* point) for point in points]
    curve1 = GeomAPI_PointsToBSpline(array1_from_points1([points[0], points[1]])).Curve()
    curve2 = GeomAPI_PointsToBSpline(array1_from_points1([points[3], points[2]])).Curve()
    srf = geomfill_Surface(curve1, curve2)
    return BRepBuilderAPI_MakeFace(srf, 1e-6).Face()


def ngon_to_face(points: NGon) -> TopoDS_Face:
    """Convert a Ngon to a BRep face with an underlying best-fit surface.

    Parameters
    ----------
    points : sequence[point]
        Points defining a polygon.

    Returns
    -------
    TopoDS_Face

    """
    points = [gp_Pnt(* point) for point in points]
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
    AssertionError
        If the mesh is not a triangle mesh.

    """
    assert mesh.is_trimesh(), "The input mesh is not a triangle mesh."

    shell = TopoDS_Shell()
    builder = BRep_Builder()
    builder.MakeShell(shell)

    for face in mesh.faces():
        points = mesh.face_coordinates(face)
        builder.Add(shell, triangle_to_face(points))

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
    AssertionError
        If the input mesh is not a quad mesh.

    """
    assert mesh.is_quadmesh(), "The input mesh is not a quad mesh."

    shell = TopoDS_Shell()
    builder = BRep_Builder()
    builder.MakeShell(shell)

    for face in mesh.faces():
        points = mesh.face_coordinates(face)
        builder.Add(shell, quad_to_face(points))

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

    """
    # https://github.com/tpaviot/pythonocc-demos/blob/master/examples/core_geometry_geomplate.py

    shell = TopoDS_Shell()
    builder = BRep_Builder()
    builder.MakeShell(shell)

    for face in mesh.faces():
        points = mesh.face_coordinates(face)

        if len(points) == 3:
            builder.Add(shell, triangle_to_face(points))
        elif len(points) == 4:
            builder.Add(shell, quad_to_face(points))
        else:
            builder.Add(shell, ngon_to_face(points))

    return shell
