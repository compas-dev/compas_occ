from OCC.Core.TopoDS import TopoDS_Solid, TopoDS_Vertex
from OCC.Core.gp import gp_Ax3, gp_Pnt, gp_Dir, gp_Vec
from OCCUtils.Common import vertex2pnt
from compas.geometry import Frame, Point, Vector, Box


def compas_vec_to_occ_dir(self: gp_Dir) -> Vector:
    return Vector(self.X(), self.Y(), self.Z())


def occ_direction_to_compas(self: gp_Dir) -> Vector:
    return Vector(self.X(), self.Y(), self.Z())


def occ_point_to_compas(self: gp_Pnt) -> Point:
    return Point(self.X(), self.Y(), self.Z())


def frame_to_occ(self: Frame) -> gp_Ax3:
    pt = self.point.to_occ()
    vX = self.xaxis.to_occ_dir()
    normal = self.normal.to_occ_dir()
    return gp_Ax3(pt, normal, vX)


def point_to_occ(self: Point) -> gp_Pnt:
    return gp_Pnt(self.x, self.y, self.z)


def gp_pnt_to_point(self: gp_Pnt) -> Point:
    return Point(self.X(), self.Y(), self.Z())


def vec_to_occ_dir(self: Point) -> gp_Pnt:
    return gp_Dir(self.x, self.y, self.z)


def occ_to_frame(self: gp_Ax3) -> Frame:
    pt = self.Location().to_compas()
    vX = self.XDirection().to_compas()
    vY = self.YDirection().to_compas()
    return Frame(pt, vX, vY)


Point.to_occ = point_to_occ
gp_Pnt.to_compas = gp_pnt_to_point
Frame.to_occ = frame_to_occ
Vector.to_occ = point_to_occ
Vector.to_occ_dir = vec_to_occ_dir
gp_Ax3.to_compas = occ_to_frame
gp_Pnt.to_compas = occ_point_to_compas
gp_Dir.to_compas = occ_direction_to_compas
gp_Dir.to_occ = compas_vec_to_occ_dir


# this is a topological entity, should go in its proper module...
# consider below this line an separate module, dealing with topological rather than primitives

def box_to_occ(self: Box) -> TopoDS_Solid:
    # in OCC the frame presents the origin of a local coordinate system
    # whereas with compas, the frame is the barycenter of of box
    from OCCUtils.Construct import make_box
    from OCCUtils.Construct import translate_topods_from_vector
    ax3 = self.frame.to_occ()
    ax2 = ax3.Ax2()
    box = make_box(ax2, self.xsize, self.ysize, self.zsize)
    # move to the barycenter
    vec = gp_Vec(-self.xsize / 2., -self.ysize / 2., -self.zsize / 2.)
    box_trns = translate_topods_from_vector(box, vec)
    return box_trns


def occ_vertex_to_point(self: TopoDS_Vertex) -> Point:
    pnt = vertex2pnt(self)
    return pnt.to_compas()


Box.to_occ = box_to_occ
TopoDS_Vertex.to_compas = occ_vertex_to_point
