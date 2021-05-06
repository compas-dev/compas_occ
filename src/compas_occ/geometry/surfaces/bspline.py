from __future__ import annotations
from operator import is_

from typing import List
from compas.geometry import Point
from compas.geometry import Transformation

from compas_occ.interop.arrays import array_of_points, array_of_floats, array_of_integers

from OCC.Core.gp import gp_Trsf
from OCC.Core.Geom import Geom_BSplineSurface


class BSplineSurface:

    def __init__(self,
                 poles: List[Point],
                 u_knots: List[float],
                 v_knots: List[float],
                 u_mults: List[int],
                 v_mults: List[int],
                 u_degree: int,
                 v_degree: int,
                 is_periodic_u: bool = False,
                 is_periodic_v: bool = False):
        self._occ_surface = Geom_BSplineSurface(
            array_of_points(poles),
            array_of_floats(u_knots),
            array_of_floats(v_knots),
            array_of_integers(u_mults),
            array_of_integers(v_mults),
            u_degree,
            v_degree,
            is_periodic_u,
            is_periodic_v
        )

    @classmethod
    def from_step(cls, filepath):
        pass

    def to_step(self, filepath):
        pass

    def __eq__(self, other: BSplineSurface) -> bool:
        return self._occ_surface.IsEqual(other._occ_surface)

    # def copy(self):
    #     return BSplineSurface(self.poles,
    #                           self.knots,
    #                           self.multiplicities,
    #                           self.degree,
    #                           self.is_periodic)

    # def transform(self, T: Transformation) -> None:
    #     _T = gp_Trsf()
    #     _T.SetValues(* T.list)
    #     self._occ_curve.Transform(T)

    # def transformed(self, T: Transformation) -> BSplineSurface:
    #     copy = self.copy()
    #     copy.transform(T)
    #     return copy
