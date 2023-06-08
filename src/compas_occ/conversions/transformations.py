import compas.geometry

from OCC.Core.gp import gp_Trsf


def compas_transformation_to_trsf(matrix: compas.geometry.Transformation):
    """Convert a COMPAS Transformation to an OCC transformation object.

    Parameters
    ----------
    matrix : :class:`~compas.geometry.Transformation`
        A COMPAS transformation to convert to OCC transformation.

    Returns
    -------
    ``gp_Trsf``

    """
    trsf = gp_Trsf()
    trsf.SetValues(*matrix.list[:12])
    return trsf
