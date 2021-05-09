from compas.geometry import Box
from compas.geometry import Translation

from OCC.Core.TopoDS import (
    TopoDS_Solid,
    TopoDS_Shell
)
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeBox
from OCC.Core.gp import (
    gp_Pnt,
    gp_Dir,
    gp_Ax2
)


class Box(Box):

    def _to_occ(self) -> BRepBuilderAPI_MakeBox:
        xaxis = self.frame.xaxis.scaled(-self.xsize)
        yaxis = self.frame.yaxis.scaled(-self.ysize)
        zaxis = self.frame.zaxis.scaled(-self.zsize)
        frame = self.frame.transformed(Translation.from_vector(xaxis + yaxis + zaxis))
        ax2 = gp_Ax2(gp_Pnt(* frame.point), gp_Dir(* frame.zaxis), gp_Dir(* frame.xaxis))
        return BRepBuilderAPI_MakeBox(ax2, self.xsize, self.ysize, self.zsize)

    def to_occ_solid(self) -> TopoDS_Solid:
        """Convert a COMPAS box shape to an OCC solid."""
        return self._to_occ.Solid()

    def to_occ_shell(self) -> TopoDS_Shell:
        """Convert a COMPAS box shape to an OCC shell."""
        return self._to_occ.Shell()
