import compas.geometry

from OCC.Core.gp import gp_Trsf


def compas_transformation_to_trsf(matrix: compas.geometry.Transformation):
    trsf = gp_Trsf()
    trsf.SetValues(*matrix.list[:12])
    return trsf
