from itertools import product

from typing import Generator, Optional, Tuple, List, Dict

import numpy as np

from compas.geometry import Point, Vector, Line, Frame, Box
from compas.geometry import Transformation
from compas.utilities import meshgrid, linspace, flatten
from compas.datastructures import Mesh

from compas_occ.conversions import compas_line_to_occ_line
from compas_occ.conversions import compas_point_from_occ_point
from compas_occ.conversions import compas_point_to_occ_point
from compas_occ.conversions import compas_vector_from_occ_vector
from compas_occ.conversions import compas_vector_to_occ_vector
from compas_occ.conversions import compas_frame_from_occ_position
from compas_occ.conversions import array2_from_points2
from compas_occ.conversions import array1_from_floats1
from compas_occ.conversions import array2_from_floats2
from compas_occ.conversions import array1_from_integers1
from compas_occ.conversions import floats2_from_array2
from compas_occ.conversions import points2_from_array2

from ..curves import NurbsCurve
from ._surface import Surface

from OCC.Core.gp import gp_Trsf
from OCC.Core.gp import gp_Pnt
from OCC.Core.gp import gp_Vec
from OCC.Core.Geom import Geom_BSplineSurface
from OCC.Core.Geom import Geom_Line
from OCC.Core.GeomAPI import GeomAPI_IntCS
from OCC.Core.GeomAPI import GeomAPI_ProjectPointOnSurf
from OCC.Core.GeomLProp import GeomLProp_SLProps
from OCC.Core.TopoDS import topods_Face
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.TopoDS import TopoDS_Face
from OCC.Core.BRep import BRep_Tool_Surface
from OCC.Core.GeomFill import GeomFill_BSplineCurves
from OCC.Core.GeomFill import GeomFill_CoonsStyle
from OCC.Core.GeomAdaptor import GeomAdaptor_Surface
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.Bnd import Bnd_OBB
from OCC.Core.BndLib import BndLib_AddSurface_Add
from OCC.Core.BndLib import BndLib_AddSurface_AddOptimal
from OCC.Core.BRepBndLib import brepbndlib_AddOBB

Point.from_occ = classmethod(compas_point_from_occ_point)
Point.to_occ = compas_point_to_occ_point
Vector.from_occ = classmethod(compas_vector_from_occ_vector)
Vector.to_occ = compas_vector_to_occ_vector
Frame.from_occ = classmethod(compas_frame_from_occ_position)
Line.to_occ = compas_line_to_occ_line


class Points:
    def __init__(self, surface):
        self.occ_surface = surface

    @property
    def points(self):
        return points2_from_array2(self.occ_surface.Poles())

    def __getitem__(self, index):
        try:
            u, v = index
        except TypeError:
            return self.points[index]
        else:
            pnt = self.occ_surface.Pole(u + 1, v + 1)
            return Point.from_occ(pnt)

    def __setitem__(self, index, point):
        u, v = index
        self.occ_surface.SetPole(u + 1, v + 1, point.to_occ())

    def __len__(self):
        return self.occ_surface.NbVPoles()
        # return self.occ_surface.Poles().NbColumns()

    def __iter__(self):
        return iter(self.points)


class NurbsSurface(Surface):
    """Class representing a NURBS surface based on the BSplineSurface of the OCC geometry kernel.

    Attributes
    ----------
    points: List[Point]
        The control points of the surface.
    weights: List[float]
        The weights of the control points.
    u_knots: List[float]
        The knot vector, in the U direction, without duplicates.
    v_knots: List[float]
        The knot vector, in the V direction, without duplicates.
    u_mults: List[int]
        The multiplicities of the knots in the knot vector of the U direction.
    v_mults: List[int]
        The multiplicities of the knots in the knot vector of the V direction.
    u_degree: int
        The degree of the polynomials in the U direction.
    v_degree: int
        The degree of the polynomials in the V direction.
    u_domain: Tuple[float, float]
        The parameter domain in the U direction.
    v_domain: Tuple[float, float]
        The parameter domain in the V direction.
    is_u_periodic: bool
        True if the curve is periodic in the U direction.
    is_v_periodic: bool
        True if the curve is periodic in the V direction.

    """

    @property
    def DATASCHEMA(self):
        from schema import Schema
        from compas.data import is_float3
        from compas.data import is_sequence_of_int
        from compas.data import is_sequence_of_float
        return Schema({
            'points': lambda points: all(is_float3(point) for point in points),
            'weights': is_sequence_of_float,
            'u_knots': is_sequence_of_float,
            'v_knots': is_sequence_of_float,
            'u_mults': is_sequence_of_int,
            'v_mults': is_sequence_of_int,
            'u_degree': int,
            'v_degree': int,
            'is_u_periodic': bool,
            'is_v_periodic': bool
        })

    @property
    def JSONSCHEMANAME(self):
        raise NotImplementedError

    def __init__(self, name: str = None) -> None:
        super().__init__(name=name)
        self.occ_surface = None
        self._points = None

    def __eq__(self, other: 'NurbsSurface') -> bool:
        for a, b in zip(flatten(self.points), flatten(other.points)):
            if a != b:
                return False
        for a, b in zip(flatten(self.weights), flatten(other.weights)):
            if a != b:
                return False
        for a, b in zip(self.u_knots, self.v_knots):
            if a != b:
                return False
        for a, b in zip(self.u_mults, self.v_mults):
            if a != b:
                return False
        if self.u_degree != self.v_degree:
            return False
        if self.is_u_periodic != self.is_v_periodic:
            return False
        return True

    def __str__(self):
        lines = [
            'NurbsSurface',
            '--------------',
            f'Points: {self.points}',
            f'Weights: {self.weights}',
            f'U Knots: {self.u_knots}',
            f'V Knots: {self.v_knots}',
            f'U Mults: {self.u_mults}',
            f'V Mults: {self.v_mults}',
            f'U Degree: {self.u_degree}',
            f'V Degree: {self.v_degree}',
            f'U Domain: {self.u_domain}',
            f'V Domain: {self.v_domain}',
            f'U Periodic: {self.is_u_periodic}',
            f'V Periodic: {self.is_v_periodic}',
        ]
        return "\n".join(lines)

    # ==============================================================================
    # Data
    # ==============================================================================

    @property
    def data(self) -> Dict:
        return {
            'points': [[point.data for point in row] for row in self.points],
            'weights': self.weights,
            'u_knots': self.u_knots,
            'v_knots': self.v_knots,
            'u_mults': self.u_mults,
            'v_mults': self.v_mults,
            'u_degree': self.u_degree,
            'v_degree': self.v_degree,
            'is_u_periodic': self.is_u_periodic,
            'is_v_periodic': self.is_v_periodic
        }

    @data.setter
    def data(self, data: Dict):
        points = [[Point.from_data(point) for point in row] for row in data['points']]
        weights = data['weights']
        u_knots = data['u_knots']
        v_knots = data['v_knots']
        u_mults = data['u_mults']
        v_mults = data['v_mults']
        u_degree = data['u_degree']
        v_degree = data['v_degree']
        is_u_periodic = data['is_u_periodic']
        is_v_periodic = data['is_v_periodic']
        self.occ_surface = Geom_BSplineSurface(
            array2_from_points2(points),
            array1_from_floats1(weights),
            array1_from_floats1(u_knots),
            array1_from_floats1(v_knots),
            array1_from_integers1(u_mults),
            array1_from_integers1(v_mults),
            u_degree,
            v_degree,
            is_u_periodic,
            is_v_periodic
        )

    @classmethod
    def from_data(cls, data: Dict) -> 'NurbsSurface':
        """Construct a BSpline surface from its data representation.

        Parameters
        ----------
        data : dict
            The data dictionary.

        Returns
        -------
        :class:`compas_occ.geometry.NurbsSurface`
            The constructed surface.

        """
        points = [[Point.from_data(point) for point in row] for row in data['points']]
        weights = data['weights']
        u_knots = data['u_knots']
        v_knots = data['v_knots']
        u_mults = data['u_mults']
        v_mults = data['v_mults']
        u_degree = data['u_degree']
        v_degree = data['v_degree']
        is_u_periodic = data['is_u_periodic']
        is_v_periodic = data['is_v_periodic']
        return NurbsSurface.from_parameters(
            points,
            weights,
            u_knots, v_knots,
            u_mults, v_mults,
            u_degree, v_degree,
            is_u_periodic, is_v_periodic
        )

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_occ(cls, occ_surface: Geom_BSplineSurface) -> 'NurbsSurface':
        """Construct a NUBRS surface from an existing OCC BSplineSurface."""
        surface = cls()
        surface.occ_surface = occ_surface
        return surface

    @classmethod
    def from_parameters(cls,
                        points: List[List[Point]],
                        weights: List[List[float]],
                        u_knots: List[float],
                        v_knots: List[float],
                        u_mults: List[int],
                        v_mults: List[int],
                        u_degree: int,
                        v_degree: int,
                        is_u_periodic: bool = False,
                        is_v_periodic: bool = False) -> 'NurbsSurface':
        """Construct a NURBS surface from explicit parameters."""
        surface = cls()
        surface.occ_surface = Geom_BSplineSurface(
            array2_from_points2(points),
            array2_from_floats2(weights),
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
    def from_points(cls,
                    points: List[List[Point]],
                    u_degree: int = 3,
                    v_degree: int = 3) -> 'NurbsSurface':
        """Construct a NURBS surface from control points."""
        u = len(points[0])
        v = len(points)
        weights = [[1.0 for _ in range(u)] for _ in range(v)]
        u_degree = u_degree if u > u_degree else u - 1
        v_degree = v_degree if v > v_degree else v - 1
        u_order = u_degree + 1
        v_order = v_degree + 1
        x = u - u_order
        u_knots = [float(i) for i in range(2 + x)]
        u_mults = [u_order]
        for _ in range(x):
            u_mults.append(1)
        u_mults.append(u_order)
        x = v - v_order
        v_knots = [float(i) for i in range(2 + x)]
        v_mults = [v_order]
        for _ in range(x):
            v_mults.append(1)
        v_mults.append(v_order)
        is_u_periodic = False
        is_v_periodic = False
        return cls.from_parameters(
            points,
            weights,
            u_knots, v_knots,
            u_mults, v_mults,
            u_degree, v_degree,
            is_u_periodic, is_v_periodic
        )

    @classmethod
    def from_meshgrid(cls, nu: int = 10, nv: int = 10) -> 'NurbsSurface':
        """Construct a NURBS surface from a mesh grid."""
        UU, VV = meshgrid(linspace(0, nu, nu + 1), linspace(0, nv, nv + 1))
        points = []
        for U, V in zip(UU, VV):
            row = []
            for u, v in zip(U, V):
                row.append(Point(u, v, 0.0))
            points.append(row)
        return cls.from_points(points=points)

    @classmethod
    def from_step(cls, filepath: str) -> 'NurbsSurface':
        """Load a NURBS surface from a STP file."""
        raise NotImplementedError

    @classmethod
    def from_face(cls, face: TopoDS_Face) -> 'NurbsSurface':
        """Construct a NURBS surface from an existing OCC TopoDS_Face."""
        srf = BRep_Tool_Surface(face)
        return cls.from_occ(srf)

    @classmethod
    def from_fill(cls, curve1: NurbsCurve, curve2: NurbsCurve) -> 'NurbsSurface':
        """Construct a NURBS surface from the infill between two NURBS curves."""
        surface = cls()
        occ_fill = GeomFill_BSplineCurves(curve1.occ_curve, curve2.occ_curve, GeomFill_CoonsStyle)
        surface.occ_surface = occ_fill.Surface()
        return surface

    # ==============================================================================
    # Conversions
    # ==============================================================================

    def to_step(self, filepath: str, schema: str = "AP203") -> None:
        """Write the surface geometry to a STP file."""
        from OCC.Core.STEPControl import STEPControl_Writer
        from OCC.Core.STEPControl import STEPControl_AsIs
        from OCC.Core.Interface import Interface_Static_SetCVal
        from OCC.Core.IFSelect import IFSelect_RetDone

        step_writer = STEPControl_Writer()
        Interface_Static_SetCVal("write.step.schema", schema)
        step_writer.Transfer(self.occ_face, STEPControl_AsIs)
        status = step_writer.Write(filepath)
        if status != IFSelect_RetDone:
            raise AssertionError("Operation failed.")

    def to_tesselation(self) -> Mesh:
        """Convert the surface to a triangle mesh."""
        from OCC.Core.Tesselator import ShapeTesselator

        tess = ShapeTesselator(self.occ_shape)
        tess.Compute()
        vertices = []
        triangles = []
        for i in range(tess.ObjGetVertexCount()):
            vertices.append(tess.GetVertex(i))
        for i in range(tess.ObjGetTriangleCount()):
            triangles.append(tess.GetTriangleIndex(i))
        return Mesh.from_vertices_and_faces(vertices, triangles)

    def to_mesh(self, nu: int = 100, nv: Optional[int] = None) -> Mesh:
        """Convert the surface to a quad mesh."""
        from itertools import product
        from functools import lru_cache

        @lru_cache(maxsize=None)
        def point_at(i, j):
            return self.point_at(i, j)

        nv = nv or nu
        V, U = np.meshgrid(self.v_space(nv + 1), self.u_space(nu + 1), indexing='ij')
        quads = [[
            point_at(U[i + 0][j + 0], V[i + 0][j + 0]),
            point_at(U[i + 0][j + 1], V[i + 0][j + 1]),
            point_at(U[i + 1][j + 1], V[i + 1][j + 1]),
            point_at(U[i + 1][j + 0], V[i + 1][j + 0])
        ] for i, j in product(range(nv), range(nu))]

        return Mesh.from_polygons(quads)

    def to_triangles(self, nu: int = 100, nv: Optional[int] = None) -> List[Tuple[float, float, float]]:
        """Convert the surface to a list of triangles."""
        from itertools import product
        from functools import lru_cache

        @lru_cache(maxsize=None)
        def point_at(i, j):
            return self.point_at(i, j)

        nv = nv or nu
        V, U = np.meshgrid(self.v_space(nv + 1), self.u_space(nu + 1), indexing='ij')

        tris = [None] * (6 * nu * nv)
        index = 0
        for i, j in product(range(nv), range(nu)):
            tris[index + 0] = point_at(U[i + 0][j + 0], V[i + 0][j + 0])
            tris[index + 1] = point_at(U[i + 0][j + 1], V[i + 0][j + 1])
            tris[index + 2] = point_at(U[i + 1][j + 1], V[i + 1][j + 1])
            tris[index + 3] = point_at(U[i + 0][j + 0], V[i + 0][j + 0])
            tris[index + 4] = point_at(U[i + 1][j + 1], V[i + 1][j + 1])
            tris[index + 5] = point_at(U[i + 1][j + 0], V[i + 1][j + 0])
            index += 6

        return tris

    # ==============================================================================
    # OCC
    # ==============================================================================

    @property
    def occ_shape(self) -> TopoDS_Shape:
        from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
        return BRepBuilderAPI_MakeFace(self.occ_surface, 1e-6).Shape()

    @property
    def occ_face(self) -> TopoDS_Face:
        return topods_Face(self.occ_shape)

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def points(self) -> List[List[Point]]:
        if not self._points:
            self._points = Points(self.occ_surface)
        return self._points

    @property
    def weights(self) -> List[List[float]]:
        weights = self.occ_surface.Weights()
        if not weights:
            weights = [[1.0] * len(self.points[0]) for _ in range(len(self.points))]
        else:
            weights = floats2_from_array2(weights)
        return weights

    @property
    def u_knots(self) -> List[float]:
        return list(self.occ_surface.UKnots())

    @property
    def v_knots(self) -> List[float]:
        return list(self.occ_surface.VKnots())

    @property
    def u_mults(self) -> List[int]:
        return list(self.occ_surface.UMultiplicities())

    @property
    def v_mults(self) -> List[int]:
        return list(self.occ_surface.VMultiplicities())

    @property
    def u_degree(self) -> int:
        return self.occ_surface.UDegree()

    @property
    def v_degree(self) -> int:
        return self.occ_surface.VDegree()

    @property
    def u_domain(self) -> int:
        umin, umax, _, _ = self.occ_surface.Bounds()
        return umin, umax

    @property
    def v_domain(self) -> int:
        _, _, vmin, vmax = self.occ_surface.Bounds()
        return vmin, vmax

    @property
    def is_u_periodic(self) -> bool:
        return self.occ_surface.IsUPeriodic()

    @property
    def is_v_periodic(self) -> bool:
        return self.occ_surface.IsVPeriodic()

    # ==============================================================================
    # Methods
    # ==============================================================================

    def copy(self) -> 'NurbsSurface':
        """Make an independent copy of the surface."""
        return NurbsSurface.from_parameters(
            self.points,
            self.weights,
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
        """Transform this surface."""
        _T = gp_Trsf()
        _T.SetValues(* T.list[:12])
        self.occ_surface.Transform(_T)

    def transformed(self, T: Transformation) -> 'NurbsSurface':
        """Transform an independent copy of this surface."""
        copy = self.copy()
        copy.transform(T)
        return copy

    def intersections_with_line(self, line: Line) -> List[Point]:
        """Compute the intersections with a line."""
        intersection = GeomAPI_IntCS(Geom_Line(line.to_occ()), self.occ_surface)
        points = []
        for index in range(intersection.NbPoints()):
            pnt = intersection.Point(index + 1)
            point = Point.from_occ(pnt)
            points.append(point)
        return points

    def u_space(self, n: int = 10) -> Generator[float, None, None]:
        """Compute evenly spaced parameters over the surface domain in the U direction.
        """
        umin, umax = self.u_domain
        return np.linspace(umin, umax, n)

    def v_space(self, n: int = 10) -> Generator[float, None, None]:
        """Compute evenly spaced parameters over the surface domain in the V direction.
        """
        vmin, vmax = self.v_domain
        return np.linspace(vmin, vmax, n)

    def u_isocurve(self, u: float) -> NurbsCurve:
        """Compute the isoparametric curve at parameter u."""
        occ_curve = self.occ_surface.UIso(u)
        return NurbsCurve.from_occ(occ_curve)

    def v_isocurve(self, v: float) -> NurbsCurve:
        """Compute the isoparametric curve at parameter v."""
        occ_curve = self.occ_surface.VIso(v)
        return NurbsCurve.from_occ(occ_curve)

    def boundary(self) -> List[NurbsCurve]:
        """Compute the boundary curves of the surface."""
        umin, umax, vmin, vmax = self.occ_surface.Bounds()
        curves = [
            self.v_isocurve(vmin),
            self.u_isocurve(umax),
            self.v_isocurve(vmax),
            self.u_isocurve(umin)
        ]
        curves[-2].reverse()
        curves[-1].reverse()
        return curves

    def xyz(self, nu: int = 10, nv: int = 10) -> List[Point]:
        """Compute point locations corresponding to evenly spaced parameters over the surface domain.
        """
        U, V = np.meshgrid(self.u_space(nu), self.v_space(nv), indexing='ij')
        return [self.point_at(U[i, j], V[i, j]) for i, j in product(np.arange(nu), np.arange(nv))]

    def point_at(self, u: float, v: float) -> Point:
        """Compute a point on the surface.
        """
        point = self.occ_surface.Value(u, v)
        return Point.from_occ(point)

    def curvature_at(self, u: float, v: float) -> Tuple[float, float, Point, Vector]:
        """Compute the curvature at a point on the surface.
        """
        props = GeomLProp_SLProps(self.occ_surface, u, v, 2, 1e-6)
        gaussian = props.GaussianCurvature()
        mean = props.MeanCurvature()
        point = props.Value()
        normal = props.Normal()
        return gaussian, mean, point, normal

    def frame_at(self, u: float, v: float) -> Frame:
        """Compute the local frame at a point on the curve.
        """
        point = gp_Pnt()
        uvec = gp_Vec()
        vvec = gp_Vec()
        self.occ_surface.D1(u, v, point, uvec, vvec)
        return Frame(Point.from_occ(point), Vector.from_occ(uvec), Vector.from_occ(vvec))

    def closest_point(self, point, distance=None) -> Point:
        """Compute the closest point on the curve to a given point.
        """
        projector = GeomAPI_ProjectPointOnSurf(point.to_occ(), self.occ_surface)
        pnt = projector.NearestPoint()
        return Point.from_occ(pnt)

    def aabb(self, precision: float = 0.0, optimal: bool = False) -> Box:
        """Compute the axis aligned bounding box of the surface."""
        box = Bnd_Box()
        if optimal:
            add = BndLib_AddSurface_AddOptimal
        else:
            add = BndLib_AddSurface_Add
        add(GeomAdaptor_Surface(self.occ_surface), precision, box)
        return Box.from_diagonal((
            Point.from_occ(box.CornerMin()),
            Point.from_occ(box.CornerMax())
        ))

    def obb(self, precision: float = 0.0) -> Box:
        """Compute the oriented bounding box of the surface."""
        box = Bnd_OBB()
        brepbndlib_AddOBB(self.occ_shape, box, True, True, True)
        return Box(Frame.from_occ(box.Position()), box.XHSize(), box.YHSize(), box.ZHSize())
