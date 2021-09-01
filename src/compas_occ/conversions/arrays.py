from typing import List

from compas.geometry import Point

from OCC.Core.gp import gp_Pnt
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.TColgp import TColgp_Array2OfPnt
from OCC.Core.TColgp import TColgp_HArray1OfPnt
from OCC.Core.TColStd import TColStd_Array1OfReal
from OCC.Core.TColStd import TColStd_Array2OfReal
from OCC.Core.TColStd import TColStd_Array1OfInteger


def array1_from_points1(points: List[Point]) -> TColgp_Array1OfPnt:
    """Construct a one-dimensional point array from a list of points."""
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
    """Construct a list of points from a one-dimensional point array."""
    return [Point(point.X(), point.Y(), point.Z()) for point in array]


def array2_from_points2(points: List[List[Point]]) -> TColgp_Array2OfPnt:
    """Construct a two-dimensional point array from a list of lists of points."""
    points = list(zip(* points))
    rows = len(points)
    cols = len(points[0])
    array = TColgp_Array2OfPnt(1, rows, 1, cols)
    for i, row in enumerate(points):
        for j, point in enumerate(row):
            array.SetValue(i + 1, j + 1, gp_Pnt(* point))
    return array


def points2_from_array2(array: TColgp_Array2OfPnt) -> List[List[Point]]:
    """Construct a list of lists of points from two-dimensional point array."""
    points = [[None for j in range(array.NbRows())] for i in range(array.NbColumns())]
    for i in range(array.LowerCol(), array.UpperCol() + 1):
        for j in range(array.LowerRow(), array.UpperRow() + 1):
            pnt = array.Value(j, i)
            points[i - 1][j - 1] = Point(pnt.X(), pnt.Y(), pnt.Z())
    return points


def array1_from_integers1(numbers: List[int]) -> TColStd_Array1OfInteger:
    """Construct a one-dimensional integer array from a list of integers."""
    array = TColStd_Array1OfInteger(1, len(numbers))
    for index, number in enumerate(numbers):
        array.SetValue(index + 1, number)
    return array


def array1_from_floats1(numbers: List[float]) -> TColStd_Array1OfReal:
    """Construct a one-dimensional float array from a list of floats."""
    array = TColStd_Array1OfReal(1, len(numbers))
    for index, number in enumerate(numbers):
        array.SetValue(index + 1, number)
    return array


def array2_from_floats2(numbers: List[List[float]]) -> TColStd_Array2OfReal:
    """Construct a two-dimensional real array from a list of lists of floats."""
    numbers = list(zip(* numbers))
    rows = len(numbers)
    cols = len(numbers[0])
    array = TColStd_Array2OfReal(1, rows, 1, cols)
    for i, row in enumerate(numbers):
        for j, number in enumerate(row):
            array.SetValue(i + 1, j + 1, number)
    return array


def floats2_from_array2(array: TColStd_Array2OfReal) -> List[List[Point]]:
    """Construct a list of lists of floats from two-dimensional real array."""
    numbers = []
    for i in range(array.LowerRow(), array.UpperRow() + 1):
        row = []
        for j in range(array.LowerCol(), array.UpperCol() + 1):
            number = array.Value(i, j)
            row.append(number)
        numbers.append(row)
    return list(zip(* numbers))
