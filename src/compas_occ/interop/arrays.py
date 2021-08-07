from __future__ import annotations

from typing import Tuple, List

from compas.geometry import Point

from OCC.Core.gp import gp_Pnt
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.TColgp import TColgp_Array2OfPnt
from OCC.Core.TColgp import TColgp_HArray1OfPnt
from OCC.Core.TColStd import TColStd_Array1OfReal
from OCC.Core.TColStd import TColStd_Array1OfInteger


def array1_from_points1(points: List[Point]) -> TColgp_Array1OfPnt:
    array = TColgp_Array1OfPnt(1, len(points))
    for index, point in enumerate(points):
        array.SetValue(index + 1, gp_Pnt(* point))
    return array


def harray1_from_points1(points: List[Point]) -> TColgp_Array1OfPnt:
    array = TColgp_HArray1OfPnt(1, len(points))
    for index, point in enumerate(points):
        array.SetValue(index + 1, gp_Pnt(* point))
    return array


def points1_from_array1(array: TColgp_Array1OfPnt) -> List[Point]:
    return [Point(point.X(), point.Y(), point.Z()) for point in array]


def array2_from_points2(points: Tuple[List[Point], List[Point]]) -> TColgp_Array2OfPnt:
    points1, points2 = points
    array = TColgp_Array2OfPnt(0, len(points1) - 1, 0, 1)
    for index, point in enumerate(points1):
        array.SetValue(index, 0, gp_Pnt(* point))
    for index, point in enumerate(points2):
        array.SetValue(index, 1, gp_Pnt(* point))
    return array


def points2_from_array2(array: TColgp_Array2OfPnt) -> Tuple[List[Point], List[Point]]:
    points1 = []
    points2 = []
    for i in range(array.LowerRow(), array.UpperRow() + 1):
        point1 = array.Value(i, array.LowerCol() + 0)
        point2 = array.Value(i, array.LowerCol() + 1)
        points1.append(Point(point1.X(), point1.Y(), point1.Z()))
        points2.append(Point(point2.X(), point2.Y(), point2.Z()))
    return points1, points2


def array1_from_integers1(numbers: List[int]) -> TColStd_Array1OfInteger:
    array = TColStd_Array1OfInteger(1, len(numbers))
    for index, number in enumerate(numbers):
        array.SetValue(index + 1, number)
    return array


def array1_from_floats1(numbers: List[float]) -> TColStd_Array1OfReal:
    array = TColStd_Array1OfReal(1, len(numbers))
    for index, number in enumerate(numbers):
        array.SetValue(index + 1, number)
    return array
