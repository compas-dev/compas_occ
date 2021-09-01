from compas.geometry import Box
from compas.geometry import Sphere
from compas.geometry import Translation

from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.TopoDS import TopoDS_Solid
from OCC.Core.TopoDS import TopoDS_Shell

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere

from OCC.Core.gp import gp_Pnt
from OCC.Core.gp import gp_Dir
from OCC.Core.gp import gp_Ax2


class Box(Box):

    def _to_occ(self) -> BRepPrimAPI_MakeBox:
        xaxis = self.frame.xaxis.scaled(-0.5 * self.xsize)
        yaxis = self.frame.yaxis.scaled(-0.5 * self.ysize)
        zaxis = self.frame.zaxis.scaled(-0.5 * self.zsize)
        frame = self.frame.transformed(Translation.from_vector(xaxis + yaxis + zaxis))
        ax2 = gp_Ax2(gp_Pnt(* frame.point), gp_Dir(* frame.zaxis), gp_Dir(* frame.xaxis))
        return BRepPrimAPI_MakeBox(ax2, self.xsize, self.ysize, self.zsize)

    def to_occ_shape(self) -> TopoDS_Shape:
        """Convert a COMPAS box to an OCC shape."""
        return self._to_occ().Shape()

    def to_occ_solid(self) -> TopoDS_Solid:
        """Convert a COMPAS box to an OCC solid."""
        return self._to_occ().Solid()

    def to_occ_shell(self) -> TopoDS_Shell:
        """Convert a COMPAS box to an OCC shell."""
        return self._to_occ().Shell()


class Sphere(Sphere):

    def _to_occ(self) -> BRepPrimAPI_MakeSphere:
        return BRepPrimAPI_MakeSphere(gp_Pnt(* self.point), self.radius)

    def to_occ_shape(self) -> TopoDS_Shape:
        """Convert a COMPAS sphere to an OCC shape."""
        return self._to_occ().Shape()

    def to_occ_solid(self) -> TopoDS_Solid:
        """Convert a COMPAS sphere to an OCC solid."""
        return self._to_occ().Solid()

    def to_occ_shell(self) -> TopoDS_Shell:
        """Convert a COMPAS sphere to an OCC shell."""
        return self._to_occ().Shell()
