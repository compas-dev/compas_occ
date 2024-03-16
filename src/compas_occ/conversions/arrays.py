from typing import List

from compas.geometry import Point
from OCC.Core.gp import gp_Pnt
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.TColgp import TColgp_Array2OfPnt
from OCC.Core.TColgp import TColgp_HArray1OfPnt
from OCC.Core.TColStd import TColStd_Array1OfInteger
from OCC.Core.TColStd import TColStd_Array1OfReal
from OCC.Core.TColStd import TColStd_Array2OfReal


def array1_from_points1(points: List[Point]) -> TColgp_Array1OfPnt:
    """Construct a one-dimensional point array from a list of points.

    Parameters
    ----------
    points : list[:class:`~compas.geometry.Point`]

    Returns
    -------
    TColgp_Array1OfPnt

    See Also
    --------
    :func:`harray1_from_points1`
    :func:`points1_from_array1`
    :func:`compas_occ.conversions.point_to_compas`

    Examples
    --------
    >>> from compas.geometry import Point
    >>> from compas_occ.conversions import array1_from_points1

    >>> points1 = [Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0)]
    >>> array1 = array1_from_points1(points1)
    >>> array1  # doctest: +ELLIPSIS
    <OCC.Core.TColgp.TColgp_Array1OfPnt; ... >

    >>> for item in array1:
    ...     print(item)
    <class 'gp_Pnt'>
    <class 'gp_Pnt'>
    <class 'gp_Pnt'>

    >>> for item in array1:
    ...     print(item.X(), item.Y(), item.Z())
    0.0 0.0 0.0
    1.0 0.0 0.0
    2.0 0.0 0.0

    """
    array = TColgp_Array1OfPnt(1, len(points))
    for index, point in enumerate(points):
        array.SetValue(index + 1, gp_Pnt(*point))
    return array


def harray1_from_points1(points: List[Point]) -> TColgp_HArray1OfPnt:
    """Construct a horizontal one-dimensional point array from a list of points.

    Parameters
    ----------
    points : list[:class:`~compas.geometry.Point`]

    Returns
    -------
    TColgp_HArray1OfPnt

    See Also
    --------
    :func:`array1_from_points1`
    :func:`compas_occ.conversions.point_to_occ`

    Examples
    --------
    >>> from compas.geometry import Point
    >>> from compas_occ.conversions import harray1_from_points1

    >>> points1 = [Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0)]
    >>> harray1 = harray1_from_points1(points1)
    >>> harray1  # doctest: +ELLIPSIS
    <OCC.Core.TColgp.TColgp_HArray1OfPnt; ... >

    >>> for item in harray1:
    ...     print(item)
    <class 'gp_Pnt'>
    <class 'gp_Pnt'>
    <class 'gp_Pnt'>

    >>> for item in harray1:
    ...     print(item.X(), item.Y(), item.Z())
    0.0 0.0 0.0
    1.0 0.0 0.0
    2.0 0.0 0.0

    """
    array = TColgp_HArray1OfPnt(1, len(points))
    for index, point in enumerate(points):
        array.SetValue(index + 1, gp_Pnt(*point))
    return array


def points1_from_array1(array: TColgp_Array1OfPnt) -> List[Point]:
    """Construct a list of points from a one-dimensional point array.

    Parameters
    ----------
    array : TColgp_Array1OfPnt

    Returns
    -------
    list[:class:`~compas.geometry.Point`]

    See Also
    --------
    :func:`array1_from_points1`
    :func:`compas_occ.conversions.point_to_compas`

    Examples
    --------
    >>> from compas_occ.conversions import points1_from_array1
    >>> from OCC.Core.TColgp import TColgp_Array1OfPnt
    >>> from OCC.Core.gp import gp_Pnt

    >>> array1 = TColgp_Array1OfPnt(1, 3)
    >>> array1.SetValue(1, gp_Pnt(0, 0, 0))
    >>> array1.SetValue(2, gp_Pnt(1, 0, 0))
    >>> array1.SetValue(3, gp_Pnt(2, 0, 0))

    >>> points1 = points1_from_array1(array1)
    >>> for point in points1:
    ...     print(point)
    Point(x=0.0, y=0.0, z=0.0)
    Point(x=1.0, y=0.0, z=0.0)
    Point(x=2.0, y=0.0, z=0.0)

    """
    return [Point(point.X(), point.Y(), point.Z()) for point in array]


def array2_from_points2(points: List[List[Point]]) -> TColgp_Array2OfPnt:
    """Construct a two-dimensional point array from a list of lists of points.

    Parameters
    ----------
    points : list[list[:class:`~compas.geometry.Point`]]

    Returns
    -------
    TColgp_Array2OfPnt

    See Also
    --------
    :func:`points2_from_array2`
    :func:`compas_occ.conversions.point_to_occ`

    Examples
    --------
    >>> from itertools import product
    >>> from compas.geometry import Point
    >>> from compas_occ.conversions import array2_from_points2

    >>> points2 = [
    ...     [Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0)],
    ...     [Point(0, 1, 0), Point(1, 1, 0), Point(2, 1, 0)],
    ... ]
    >>> array2 = array2_from_points2(points2)
    >>> array2  # doctest: +ELLIPSIS
    <OCC.Core.TColgp.TColgp_Array2OfPnt; ... >

    >>> rows = range(array2.LowerRow(), array2.UpperRow() + 1)
    >>> cols = range(array2.LowerCol(), array2.UpperCol() + 1)
    >>> for i, j in product(rows, cols):
    ...     value = array2.Value(i, j)
    ...     x = value.X()
    ...     y = value.Y()
    ...     z = value.Z()
    ...     print(x, y, z)
    0.0 0.0 0.0
    0.0 1.0 0.0
    1.0 0.0 0.0
    1.0 1.0 0.0
    2.0 0.0 0.0
    2.0 1.0 0.0

    """
    points = list(zip(*points))
    rows = len(points)
    cols = len(points[0])
    array = TColgp_Array2OfPnt(1, rows, 1, cols)
    for i, row in enumerate(points):
        for j, point in enumerate(row):
            array.SetValue(i + 1, j + 1, gp_Pnt(*point))
    return array


def points2_from_array2(array: TColgp_Array2OfPnt) -> List[List[Point]]:
    """Construct a list of lists of points from two-dimensional point array.

    Parameters
    ----------
    array : TColgp_Array2OfPnt

    Returns
    -------
    list[list[:class:`~compas.geometry.Point`]]

    See Also
    --------
    :func:`array2_from_points2`
    :func:`compas_occ.conversions.point_to_compas`

    Examples
    --------
    >>> from itertools import product
    >>> from OCC.Core.TColgp import TColgp_Array2OfPnt
    >>> from OCC.Core.gp import gp_Pnt

    >>> array2 = TColgp_Array2OfPnt(1, 2, 1, 3)
    >>> array2.SetValue(1, 1, gp_Pnt(0, 0, 0))
    >>> array2.SetValue(1, 2, gp_Pnt(1, 0, 0))
    >>> array2.SetValue(1, 3, gp_Pnt(2, 0, 0))
    >>> array2.SetValue(2, 1, gp_Pnt(0, 1, 0))
    >>> array2.SetValue(2, 2, gp_Pnt(1, 1, 0))
    >>> array2.SetValue(2, 3, gp_Pnt(2, 1, 0))

    >>> points2 = points2_from_array2(array2)
    >>> for i, j in product(range(len(points2)), range(len(points2[0]))):
    ...     print(points2[i][j])
    Point(x=0.0, y=0.0, z=0.0)
    Point(x=0.0, y=1.0, z=0.0)
    Point(x=1.0, y=0.0, z=0.0)
    Point(x=1.0, y=1.0, z=0.0)
    Point(x=2.0, y=0.0, z=0.0)
    Point(x=2.0, y=1.0, z=0.0)

    """
    points = [[None for j in range(array.NbRows())] for i in range(array.NbColumns())]
    for i in range(array.LowerCol(), array.UpperCol() + 1):
        for j in range(array.LowerRow(), array.UpperRow() + 1):
            pnt = array.Value(j, i)
            points[i - 1][j - 1] = Point(pnt.X(), pnt.Y(), pnt.Z())  # type: ignore
    return points  # type: ignore


def array1_from_integers1(numbers: List[int]) -> TColStd_Array1OfInteger:
    """Construct a one-dimensional integer array from a list of integers.

    Parameters
    ----------
    numbers : list[int]

    Returns
    -------
    TColStd_Array1OfInteger

    See Also
    --------
    :func:`array1_from_floats1`

    Examples
    --------
    >>> from compas_occ.conversions import array1_from_integers1
    >>> integers1 = [0, 1, 2]
    >>> array1 = array1_from_integers1(integers1)
    >>> array1  # doctest: +ELLIPSIS
    <OCC.Core.TColStd.TColStd_Array1OfInteger; ... >

    """
    array = TColStd_Array1OfInteger(1, len(numbers))
    for index, number in enumerate(numbers):
        array.SetValue(index + 1, number)
    return array


def array1_from_floats1(numbers: List[float]) -> TColStd_Array1OfReal:
    """Construct a one-dimensional float array from a list of floats.

    Parameters
    ----------
    numbers : list[float]

    Returns
    -------
    TColStd_Array1OfReal

    See Also
    --------
    :func:`array1_from_integers1`
    :func:`array2_from_floats2`

    Examples
    --------
    >>> from compas_occ.conversions import array1_from_floats1
    >>> floats1 = [0.0, 1.0, 2.0]
    >>> array1 = array1_from_floats1(floats1)
    >>> array1  # doctest: +ELLIPSIS
    <OCC.Core.TColStd.TColStd_Array1OfReal; ... >

    """
    array = TColStd_Array1OfReal(1, len(numbers))
    for index, number in enumerate(numbers):
        array.SetValue(index + 1, number)
    return array


def array2_from_floats2(numbers: List[List[float]]) -> TColStd_Array2OfReal:
    """Construct a two-dimensional real array from a list of lists of floats.

    Parameters
    ----------
    numbers : list[list[float]]

    Returns
    -------
    TColStd_Array2OfReal

    See Also
    --------
    :func:`array1_from_floats1`

    Examples
    --------
    >>> from compas_occ.conversions import array2_from_floats2
    >>> floats2 = [
    ...     [0.0, 0.0, 0.0],
    ...     [1.0, 0.0, 0.0],
    ...     [2.0, 0.0, 0.0],
    ... ]
    >>> array2 = array2_from_floats2(floats2)
    >>> array2  # doctest: +ELLIPSIS
    <OCC.Core.TColStd.TColStd_Array2OfReal; ... >

    """
    numbers = list(zip(*numbers))
    rows = len(numbers)
    cols = len(numbers[0])
    array = TColStd_Array2OfReal(1, rows, 1, cols)
    for i, row in enumerate(numbers):
        for j, number in enumerate(row):
            array.SetValue(i + 1, j + 1, number)
    return array


def floats2_from_array2(array: TColStd_Array2OfReal) -> List[List[Point]]:
    """Construct a list of lists of floats from two-dimensional real array.

    Parameters
    ----------
    array : TColStd_Array2OfReal

    Returns
    -------
    list[list[float]]

    See Also
    --------
    :func:`array2_from_floats2`

    Examples
    --------
    >>> from itertools import product
    >>> from OCC.Core.TColStd import TColStd_Array2OfReal

    >>> array2 = TColStd_Array2OfReal(1, 2, 1, 3)
    >>> array2.SetValue(1, 1, 0.0)
    >>> array2.SetValue(1, 2, 1.0)
    >>> array2.SetValue(1, 3, 2.0)
    >>> array2.SetValue(2, 1, 0.0)
    >>> array2.SetValue(2, 2, 1.0)
    >>> array2.SetValue(2, 3, 2.0)

    >>> floats2 = floats2_from_array2(array2)
    >>> floats2
    [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)]

    """
    numbers = []
    for i in range(array.LowerRow(), array.UpperRow() + 1):
        row = []
        for j in range(array.LowerCol(), array.UpperCol() + 1):
            number = array.Value(i, j)
            row.append(number)
        numbers.append(row)
    return list(zip(*numbers))
