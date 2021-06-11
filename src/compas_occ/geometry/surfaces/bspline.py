from __future__ import annotations

from typing import Optional, Tuple, List

from compas.geometry import Point, Vector, Line, Frame, Box
from compas.geometry import Transformation
from compas.utilities import meshgrid, linspace, flatten
from compas.datastructures import Mesh

from compas_occ.interop.primitives import (
    compas_line_to_occ_line,
    compas_point_from_occ_point,
    compas_point_to_occ_point,
    compas_vector_from_occ_vector,
    compas_vector_to_occ_vector
)
from compas_occ.interop.arrays import (
    array2_from_points2,
    array1_from_floats1,
    array1_from_integers1,
    points2_from_array2
)
from compas_occ.geometry.curves import BSplineCurve

from OCC.Core.gp import (
    gp_Trsf,
    gp_Pnt,
    gp_Vec
)
from OCC.Core.Geom import (
    Geom_BSplineSurface,
    Geom_Line
)
from OCC.Core.GeomAPI import GeomAPI_IntCS
from OCC.Core.TopoDS import (
    topods_Face,
    TopoDS_Shape,
    TopoDS_Face
)
from OCC.Core.BRep import BRep_Tool_Surface
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


Point.from_occ = classmethod(compas_point_from_occ_point)
Point.to_occ = compas_point_to_occ_point

Vector.from_occ = classmethod(compas_vector_from_occ_vector)
Vector.to_occ = compas_vector_to_occ_vector

Line.to_occ = compas_line_to_occ_line


class BSplineSurface:

    def __init__(self):
        self.occ_surface = None

    def __eq__(self, other: BSplineSurface) -> bool:
        return self.occ_surface.IsEqual(other.occ_surface)

    @classmethod
    def from_occ(cls, occ_surface: Geom_BSplineSurface) -> BSplineSurface:
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
    def from_points(cls, points: List[Point]) -> BSplineSurface:
        raise NotImplementedError

    @classmethod
    def from_step(cls, filepath: str) -> BSplineSurface:
        raise NotImplementedError

    @classmethod
    def from_face(cls, face: TopoDS_Face) -> BSplineSurface:
        srf = BRep_Tool_Surface(face)
        return cls.from_occ(srf)

    @classmethod
    def from_fill(cls, curve1: BSplineCurve, curve2: BSplineCurve) -> BSplineSurface:
        surface = cls()
        occ_fill = GeomFill_BSplineCurves(curve1.occ_curve, curve2.occ_curve, GeomFill_CoonsStyle)
        surface.occ_surface = occ_fill.Surface()
        return surface

    def to_step(self, filepath: str, schema: str = "AP203") -> None:
        step_writer = STEPControl_Writer()
        Interface_Static_SetCVal("write.step.schema", schema)
        step_writer.Transfer(self.occ_face, STEPControl_AsIs)
        status = step_writer.Write(filepath)
        if status != IFSelect_RetDone:
            raise AssertionError("Operation failed.")

    def to_tesselation(self) -> Mesh:
        tess = ShapeTesselator(self.occ_shape)
        tess.Compute()
        vertices = []
        triangles = []
        for i in range(tess.ObjGetVertexCount()):
            vertices.append(tess.GetVertex(i))
        for i in range(tess.ObjGetTriangleCount()):
            triangles.append(tess.GetTriangleIndex(i))
        return Mesh.from_vertices_and_faces(vertices, triangles)

    def to_vizmesh(self, u: int = 100, v: Optional[int] = None) -> Mesh:
        quads = []
        v = v or u
        U, V = meshgrid(self.uspace(u), self.vspace(v))
        for i in range(u - 1):
            for j in range(v - 1):
                a = self.point_at(U[i + 0][j + 0], V[i + 0][j + 0])
                b = self.point_at(U[i + 0][j + 1], V[i + 0][j + 1])
                c = self.point_at(U[i + 1][j + 1], V[i + 1][j + 1])
                d = self.point_at(U[i + 1][j + 0], V[i + 1][j + 0])
                quads.append([a, b, c, d])
        return Mesh.from_polygons(quads)

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

    @property
    def aabb(self) -> Box:
        pass

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

    def intersections(self, line: Line) -> List[Point]:
        intersection = GeomAPI_IntCS(Geom_Line(line.to_occ()), self.occ_surface)
        points = []
        for index in range(intersection.NbPoints()):
            pnt = intersection.Point(index + 1)
            point = Point.from_occ(pnt)
            points.append(point)
        return points

    def point_at(self, u: float, v: float) -> Point:
        point = self.occ_surface.Value(u, v)
        return Point.from_occ(point)

    def frame_at(self, u: float, v: float) -> Frame:
        point = gp_Pnt()
        uvec = gp_Vec()
        vvec = gp_Vec()
        self.occ_surface.D1(u, v, point, uvec, vvec)
        return Frame(Point.from_occ(point), Vector.from_occ(uvec), Vector.from_occ(vvec))

    def uspace(self, n: int = 10) -> List[float]:
        umin, umax, _, _ = self.occ_surface.Bounds()
        return linspace(umin, umax, n)

    def vspace(self, n: int = 10) -> List[float]:
        _, _, vmin, vmax = self.occ_surface.Bounds()
        return linspace(vmin, vmax, n)

    def xyz(self, nu: int = 10, nv: int = 10) -> List[Point]:
        U, V = meshgrid(self.uspace(nu), self.vspace(nv), 'ij')
        return [self.point_at(u, v) for u, v in zip(flatten(U), flatten(V))]
