from OCC.Core.gp import gp_Trsf

import compas.geometry


def compas_transformation_to_trsf(matrix: compas.geometry.Transformation) -> gp_Trsf:
    """Convert a COMPAS transformation to a OCC transformation.

    Parameters
    ----------
    matrix
        A COMPAS transformation.

    Returns
    -------
    gp_Trsf
        An OCC transformation.

    Examples
    --------
    >>> from compas.geometry import Translation
    >>> from compas_occ.conversions import compas_transformation_to_trsf
    >>> transformation = Translation.from_vector([1, 2, 3])
    >>> compas_transformation_to_trsf(transformation)
    <class 'gp_Trsf'>

    """
    trsf = gp_Trsf()
    trsf.SetValues(*matrix.list[:12])
    return trsf
