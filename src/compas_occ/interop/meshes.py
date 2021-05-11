from __future__ import annotations

from compas.geometry import Point
from compas.datastructures import Mesh

from compas_occ.geometry.curves import BSplineCurve
from compas_occ.geometry.surfaces import BSplineSurface

from OCC.Core.gp import gp_Pnt
from OCC.Core.TopoDS import TopoDS_Shell
from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Core.GeomFill import geomfill_Surface


def compas_trimesh_to_occ_shell(mesh: Mesh) -> TopoDS_Shell:
    """Convert a COMPAS triangle mesh to an OCC shell."""
    assert mesh.is_trimesh(), "The input mesh is not a triangle mesh."

    shell = TopoDS_Shell()
    builder = BRep_Builder()
    builder.MakeShell(shell)

    for face in mesh.faces():
        polygon = BRepBuilderAPI_MakePolygon()
        for point in mesh.face_coordinates(face):
            polygon.Add(gp_Pnt(* point))
        wire = polygon.Wire()
        face = BRepBuilderAPI_MakeFace(wire).Face()
        builder.Add(shell, face)

    return shell


def compas_quadmesh_to_occ_shell(mesh: Mesh) -> TopoDS_Shell:
    """Convert a COMPAS quad mesh to an OCC shell."""
    assert mesh.is_quadmesh(), "The input mesh is not a quad mesh."

    shell = TopoDS_Shell()
    builder = BRep_Builder()
    builder.MakeShell(shell)

    for face in mesh.faces():
        points = [Point(* point) for point in mesh.face_coordinates(face)]
        curve1 = BSplineCurve.from_points([points[0], points[1]])
        curve2 = BSplineCurve.from_points([points[3], points[2]])
        srf = geomfill_Surface(curve1.occ_curve, curve2.occ_curve)
        surface = BSplineSurface.from_occ(srf)
        face = BRepBuilderAPI_MakeFace(surface.occ_face).Face()
        builder.Add(shell, face)

    return shell


def compas_mesh_to_occ_shell(mesh: Mesh) -> TopoDS_Shell:
    """Convert a general COMPAS mesh to an OCC shell."""
    # https://github.com/tpaviot/pythonocc-demos/blob/master/examples/core_geometry_geomplate.py

    raise NotImplementedError
