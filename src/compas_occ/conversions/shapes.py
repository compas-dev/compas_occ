# from compas.geometry import Box
# from compas.geometry import Translation

# from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
# from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere

# from OCC.Core.gp import gp_Pnt
# from OCC.Core.gp import gp_Dir
# from OCC.Core.gp import gp_Ax2


# def compas_box_to_occ_box(box: Box) -> BRepPrimAPI_MakeBox:
#     """Convert a COMPAS box to an OCC box."""
#     xaxis = box.frame.xaxis.scaled(-0.5 * box.xsize)
#     yaxis = box.frame.yaxis.scaled(-0.5 * box.ysize)
#     zaxis = box.frame.zaxis.scaled(-0.5 * box.zsize)
#     frame = box.frame.transformed(Translation.from_vector(xaxis + yaxis + zaxis))
#     ax2 = gp_Ax2(gp_Pnt(*frame.point), gp_Dir(*frame.zaxis), gp_Dir(*frame.xaxis))
#     return BRepPrimAPI_MakeBox(ax2, box.xsize, box.ysize, box.zsize)
