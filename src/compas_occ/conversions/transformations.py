from math import isclose

from OCC.Core.gp import gp_Trsf

from compas.geometry._typing import TransformationType


def compas_transformation_to_trsf(matrix: TransformationType) -> gp_Trsf:
    """Convert a COMPAS transformation to a OCC transformation.

    Parameters
    ----------
    matrix
        A COMPAS transformation or a nested transformation matrix.

    Returns
    -------
    gp_Trsf
        An OCC transformation.

    Raises
    ------
    ValueError
        If the matrix is not 4x4 affine or contains a shear or nonuniform
        scale that `gp_Trsf` cannot represent exactly.

    Examples
    --------
    >>> from compas.geometry import Translation
    >>> from compas_occ.conversions import compas_transformation_to_trsf
    >>> transformation = Translation.from_vector([1, 2, 3])
    >>> compas_transformation_to_trsf(transformation)
    <class 'gp_Trsf'>

    """
    rows = [[float(value) for value in row] for row in matrix]
    if len(rows) != 4 or any(len(row) != 4 for row in rows):
        raise ValueError("An OCC transformation should be represented by a 4x4 matrix.")
    if any(not isclose(value, expected, rel_tol=1e-12, abs_tol=1e-12) for value, expected in zip(rows[3], (0.0, 0.0, 0.0, 1.0))):
        raise ValueError("Open CASCADE gp_Trsf cannot represent projective transformations.")

    values = [value for row in rows[:3] for value in row]
    trsf = gp_Trsf()
    trsf.SetValues(*values)

    converted = [trsf.Value(i, j) for i in range(1, 4) for j in range(1, 5)]
    if any(not isclose(expected, actual, rel_tol=1e-9, abs_tol=1e-12) for expected, actual in zip(values, converted)):
        raise ValueError("Open CASCADE gp_Trsf cannot represent shear or nonuniform scaling.")

    return trsf
