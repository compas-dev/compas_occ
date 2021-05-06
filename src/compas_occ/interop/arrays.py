from OCC.Core.gp import gp_Pnt

from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.TColStd import TColStd_Array1OfReal, TColStd_Array1OfInteger


def array_of_points(points):
    array = TColgp_Array1OfPnt(0, len(points) - 1)
    for index, point in enumerate(points):
        array.SetValue(index, gp_Pnt(* point))
    return array


def array_of_integers(numbers):
    array = TColStd_Array1OfInteger(0, len(numbers) - 1)
    for index, number in enumerate(numbers):
        array.SetValue(index, number)
    return array


def array_of_floats(numbers):
    array = TColStd_Array1OfReal(0, len(numbers) - 1)
    for index, number in enumerate(numbers):
        array.SetValue(index, number)
    return array
