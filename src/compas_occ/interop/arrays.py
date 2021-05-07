from OCC.Core.gp import gp_Pnt

from OCC.Core.TColgp import (
    TColgp_Array1OfPnt,
    TColgp_Array2OfPnt
)
from OCC.Core.TColStd import (
    TColStd_Array1OfReal,
    TColStd_Array1OfInteger
)


def array1_from_points1(points):
    array = TColgp_Array1OfPnt(0, len(points) - 1)
    for index, point in enumerate(points):
        array.SetValue(index, gp_Pnt(* point))
    return array


def points1_from_array1(array):
    pass


def array2_from_points2(points):
    points1, points2 = points
    array = TColgp_Array2OfPnt(0, len(points1) - 1, 0, 1)
    for index, point in enumerate(points1):
        array.SetValue(index, 0, gp_Pnt(* point))
    for index, point in enumerate(points2):
        array.SetValue(index, 1, gp_Pnt(* point))
    return array


def points2_from_array2(array):
    pass


def array1_from_integers1(numbers):
    array = TColStd_Array1OfInteger(0, len(numbers) - 1)
    for index, number in enumerate(numbers):
        array.SetValue(index, number)
    return array


def integers1_from_array1(array):
    pass


def array1_from_floats1(numbers):
    array = TColStd_Array1OfReal(0, len(numbers) - 1)
    for index, number in enumerate(numbers):
        array.SetValue(index, number)
    return array


def floats1_from_array1(array):
    pass
