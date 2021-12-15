from typing import Tuple, List, Dict, Union

import numpy as np

from compas.geometry import Point, Vector, Line, Frame, Box
from compas.geometry import Transformation
from compas.datastructures import Mesh

from compas_occ.conversions import compas_line_to_occ_line
from compas_occ.conversions import compas_point_from_occ_point
from compas_occ.conversions import compas_point_to_occ_point
from compas_occ.conversions import compas_vector_from_occ_vector
from compas_occ.conversions import compas_vector_to_occ_vector
from compas_occ.conversions import compas_frame_from_occ_position
from compas_occ.conversions import points2_from_array2

from compas_occ.geometry.curves import OCCNurbsCurve

try:
    from compas.geometry import NurbsSurface
except ImportError:
    from compas.geometry import Geometry as NurbsSurface

from OCC.Core.Geom import Geom_BSplineSurface
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.TopoDS import TopoDS_Face


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


class OCCNurbsSurface(NurbsSurface):

    def __init__(self, name: str = None) -> None: ...

    def __eq__(self, other: 'OCCNurbsSurface') -> bool: ...

    # ==============================================================================
    # Data
    # ==============================================================================

    @property
    def data(self) -> Dict: ...

    @data.setter
    def data(self, data: Dict) -> None: ...

    @classmethod
    def from_data(cls, data: Dict) -> 'OCCNurbsSurface': ...

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_occ(cls, occ_surface: Geom_BSplineSurface) -> 'OCCNurbsSurface': ...

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
                        is_v_periodic: bool = False) -> 'OCCNurbsSurface': ...

    @classmethod
    def from_points(cls,
                    points: List[List[Point]],
                    u_degree: int = 3,
                    v_degree: int = 3) -> 'OCCNurbsSurface': ...

    @classmethod
    def from_step(cls, filepath: str) -> 'OCCNurbsSurface': ...

    @classmethod
    def from_face(cls, face: TopoDS_Face) -> 'OCCNurbsSurface': ...

    @classmethod
    def from_fill(cls, curve1: OCCNurbsCurve, curve2: OCCNurbsCurve) -> 'OCCNurbsSurface': ...

    # ==============================================================================
    # Conversions
    # ==============================================================================

    def to_step(self, filepath: str, schema: str = "AP203") -> None: ...

    def to_tesselation(self) -> Mesh: ...

    # ==============================================================================
    # OCC
    # ==============================================================================

    @property
    def occ_shape(self) -> TopoDS_Shape: ...

    @property
    def occ_face(self) -> TopoDS_Face: ...

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def points(self) -> List[List[Point]]: ...

    @property
    def weights(self) -> List[List[float]]: ...

    @property
    def u_knots(self) -> List[float]: ...

    @property
    def v_knots(self) -> List[float]: ...

    @property
    def u_mults(self) -> List[int]: ...

    @property
    def v_mults(self) -> List[int]: ...

    @property
    def u_degree(self) -> int: ...

    @property
    def v_degree(self) -> int: ...

    @property
    def u_domain(self) -> int: ...

    @property
    def v_domain(self) -> int: ...

    @property
    def is_u_periodic(self) -> bool: ...

    @property
    def is_v_periodic(self) -> bool: ...

    # ==============================================================================
    # Methods
    # ==============================================================================

    def transform(self, T: Transformation) -> None: ...

    def u_isocurve(self, u: float) -> OCCNurbsCurve: ...

    def v_isocurve(self, v: float) -> OCCNurbsCurve: ...

    def boundary(self) -> List[OCCNurbsCurve]: ...

    def point_at(self, u: float, v: float) -> Point: ...

    def curvature_at(self, u: float, v: float) -> Tuple[float, float, Point, Vector]: ...

    def frame_at(self, u: float, v: float) -> Frame: ...

    def closest_point(self, point, distance=None, parameter: bool = False) -> Union[Point, Tuple[Point, float]]: ...

    def aabb(self, precision: float = 0.0, optimal: bool = False) -> Box: ...

    def obb(self, precision: float = 0.0) -> Box: ...

    def intersections_with_line(self, line: Line) -> List[Point]: ...

