from __future__ import annotations

from typing import Tuple, List
from compas.geometry import Point
from compas.geometry import Transformation
from compas.datastructures import Mesh

from compas_occ.interop.arrays import (
    array2_from_points2,
    array1_from_floats1,
    array1_from_integers1,
    points2_from_array2
)

from OCC.Core.gp import gp_Trsf
from OCC.Core.Geom import Geom_BSplineSurface
from OCC.Core.TopoDS import (
    topods_Face,
    TopoDS_Shape,
    TopoDS_Face
)
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace

from OCC.Core.TColgp import TColgp_Array2OfPnt
from OCC.Core.TColStd import (
    TColStd_Array1OfReal,
    TColStd_Array1OfInteger
)
from OCC.Core.STEPControl import (
    STEPControl_Writer,
    STEPControl_AsIs
)
from OCC.Core.Interface import Interface_Static_SetCVal
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.GeomFill import (
    GeomFill_BSplineCurves,
    GeomFill_CoonsStyle
)
from OCC.Core.Tesselator import ShapeTesselator


# update to use "data" interface
class BSplineSurface:

    def __init__(self):
        self.occ_surface = None

    def __eq__(self, other: BSplineSurface) -> bool:
        return self.occ_surface.IsEqual(other.occ_surface)

    @classmethod
    def from_occ(cls, occ_surface) -> BSplineSurface:
        surface = cls()
        surface.occ_surface = occ_surface
        return surface

    @classmethod
    def from_parameters(cls,
                        poles: Tuple[List[Point], List[Point]],
                        u_knots: List[float],
                        v_knots: List[float],
                        u_mults: List[int],
                        v_mults: List[int],
                        u_degree: int,
                        v_degree: int,
                        is_u_periodic: bool = False,
                        is_v_periodic: bool = False) -> BSplineSurface:
        surface = cls()
        surface.occ_surface = Geom_BSplineSurface(
            array2_from_points2(poles),
            array1_from_floats1(u_knots),
            array1_from_floats1(v_knots),
            array1_from_integers1(u_mults),
            array1_from_integers1(v_mults),
            u_degree,
            v_degree,
            is_u_periodic,
            is_v_periodic
        )
        return surface

    @classmethod
    def from_step(cls, filepath) -> BSplineSurface:
        pass

    def to_step(self, filepath, schema="AP203") -> None:
        step_writer = STEPControl_Writer()
        Interface_Static_SetCVal("write.step.schema", schema)
        step_writer.Transfer(self.occ_face, STEPControl_AsIs)
        status = step_writer.Write(filepath)
        if status != IFSelect_RetDone:
            raise AssertionError("Operation failed.")

    def to_vizmesh(self) -> Mesh:
        tess = ShapeTesselator(self.occ_shape)
        tess.Compute()
        vertices = []
        triangles = []
        for i in range(tess.ObjGetVertexCount()):
            vertices.append(tess.GetVertex(i))
        for i in range(tess.ObjGetTriangleCount()):
            triangles.append(tess.GetTriangleIndex(i))
        return Mesh.from_vertices_and_faces(vertices, triangles)

    @classmethod
    def from_fill(cls, curve1, curve2) -> BSplineSurface:
        surface = cls()
        occ_fill = GeomFill_BSplineCurves(curve1.occ_curve, curve2.occ_curve, GeomFill_CoonsStyle)
        surface.occ_surface = occ_fill.Surface()
        return surface

    @property
    def occ_shape(self) -> TopoDS_Shape:
        return BRepBuilderAPI_MakeFace(self.occ_surface, 1e-6).Shape()

    @property
    def occ_face(self) -> TopoDS_Face:
        return topods_Face(self.occ_shape)

    @property
    def occ_poles(self) -> TColgp_Array2OfPnt:
        return self.occ_surface.Poles()

    @property
    def occ_u_knots(self) -> TColStd_Array1OfReal:
        return self.occ_surface.UKnots()

    @property
    def occ_v_knots(self) -> TColStd_Array1OfReal:
        return self.occ_surface.VKnots()

    @property
    def occ_u_mults(self) -> TColStd_Array1OfInteger:
        return self.occ_surface.UMultiplicities()

    @property
    def occ_v_mults(self) -> TColStd_Array1OfInteger:
        return self.occ_surface.VMultiplicities()

    @property
    def poles(self) -> Tuple[List[Point], List[Point]]:
        return points2_from_array2(self.occ_poles)

    @property
    def u_knots(self) -> List[float]:
        return self.occ_u_knots

    @property
    def v_knots(self) -> List[float]:
        return self.occ_v_knots

    @property
    def u_mults(self) -> List[int]:
        return self.occ_u_mults

    @property
    def v_mults(self) -> List[int]:
        return self.occ_v_mults

    @property
    def u_degree(self) -> int:
        return self.occ_surface.UDegree()

    @property
    def v_degree(self) -> int:
        return self.occ_surface.VDegree()

    @property
    def is_u_periodic(self) -> bool:
        return self.occ_surface.IsUPeriodic()

    @property
    def is_v_periodic(self) -> bool:
        return self.occ_surface.IsVPeriodic()

    def copy(self) -> BSplineSurface:
        return BSplineSurface.from_parameters(
            self.poles,
            self.u_knots,
            self.v_knots,
            self.u_mults,
            self.v_mults,
            self.u_degree,
            self.v_degree,
            self.is_u_periodic,
            self.is_v_periodic
        )

    def transform(self, T: Transformation) -> None:
        _T = gp_Trsf()
        _T.SetValues(* T.list)
        self.occ_surface.Transform(T)

    def transformed(self, T: Transformation) -> BSplineSurface:
        copy = self.copy()
        copy.transform(T)
        return copy
