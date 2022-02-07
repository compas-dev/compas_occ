from typing import Iterable, Tuple, List, Dict, Union

from compas.geometry import Point

from compas_occ.geometry.curves import OCCNurbsCurve

from compas.geometry import NurbsSurface


class ControlPoints:

    def __init__(self, surface: 'OCCNurbsSurface') -> None: ...

    @property
    def points(self) -> List[List[Point]]: ...

    def __getitem__(self, index: Union[int, Tuple[int, int]]) -> Point: ...

    def __setitem__(self, index: Tuple[int, int], point: Point) -> None: ...

    def __len__(self) -> int: ...

    def __iter__(self) -> Iterable: ...


class OCCNurbsSurface(NurbsSurface):

    def __init__(self, name: str = None) -> None: ...

    def __eq__(self, other: 'OCCNurbsSurface') -> bool: ...

    @property
    def data(self) -> Dict: ...

    @data.setter
    def data(self, data: Dict) -> None: ...

    @classmethod
    def from_data(cls, data: Dict) -> 'OCCNurbsSurface': ...

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
    def from_fill(cls, curve1: OCCNurbsCurve, curve2: OCCNurbsCurve) -> 'OCCNurbsSurface': ...

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
