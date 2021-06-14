from __future__ import annotations
from typing import List
from typing_extensions import Annotated

import compas.geometry
from compas.geometry import Point
from compas.datastructures import Mesh

from compas_occ.geometry.curves import BSplineCurve
from compas_occ.geometry.surfaces import BSplineSurface

from OCC.Core.gp import gp_Pnt
from OCC.Core.TopoDS import TopoDS_Shell
from OCC.Core.TopoDS import TopoDS_Face
from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Core.GeomFill import geomfill_Surface
from OCC.Core.BRepFill import BRepFill_Filling
from OCC.Core.GeomAbs import GeomAbs_C0
from OCC.Extend.TopologyUtils import TopologyExplorer


def triangle_to_face(points: List[compas.geometry.Point, Annotated[List[float], 3]]) -> TopoDS_Face:
    polygon = BRepBuilderAPI_MakePolygon()
    for point in points:
        polygon.Add(gp_Pnt(* point))
    polygon.Close()
    wire = polygon.Wire()
    return BRepBuilderAPI_MakeFace(wire).Face()


def quad_to_face(points: List[compas.geometry.Point, Annotated[List[float], 3]]) -> TopoDS_Face:
    points = [Point(* point) for point in points]
    curve1 = BSplineCurve.from_points([points[0], points[1]])
    curve2 = BSplineCurve.from_points([points[3], points[2]])
    srf = geomfill_Surface(curve1.occ_curve, curve2.occ_curve)
    surface = BSplineSurface.from_occ(srf)
    return BRepBuilderAPI_MakeFace(surface.occ_face).Face()


def ngon_to_face(points: List[compas.geometry.Point, Annotated[List[float], 3]]) -> TopoDS_Face:
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
    """Convert a COMPAS triangle mesh to an OCC shell."""
    assert mesh.is_trimesh(), "The input mesh is not a triangle mesh."

    shell = TopoDS_Shell()
    builder = BRep_Builder()
    builder.MakeShell(shell)

    for face in mesh.faces():
        points = mesh.face_coordinates(face)
        builder.Add(shell, triangle_to_face(points))

    return shell


def compas_quadmesh_to_occ_shell(mesh: Mesh) -> TopoDS_Shell:
    """Convert a COMPAS quad mesh to an OCC shell."""
    assert mesh.is_quadmesh(), "The input mesh is not a quad mesh."

    shell = TopoDS_Shell()
    builder = BRep_Builder()
    builder.MakeShell(shell)

    for face in mesh.faces():
        points = mesh.face_coordinates(face)
        builder.Add(shell, quad_to_face(points))

    return shell


def compas_mesh_to_occ_shell(mesh: Mesh) -> TopoDS_Shell:
    """Convert a general COMPAS mesh to an OCC shell."""
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
