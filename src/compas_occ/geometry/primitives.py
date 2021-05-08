from compas.geometry import (
    Point,
    Vector,
    Line
)

from OCC.Core.gp import (
    gp_Pnt,
    gp_Vec,
    gp_Dir,
    gp_Lin
)


def compas_point_to_occ_point(self: Point) -> gp_Pnt:
    return gp_Pnt(* self)


@classmethod
def compas_point_from_occ_point(cls: Point, point: gp_Pnt) -> Point:
    return cls(point.X(), point.Y(), point.Z())


def compas_vector_to_occ_vector(self: Vector) -> gp_Vec:
    return gp_Vec(* self)


def compas_vector_to_occ_direction(self: Vector) -> gp_Dir:
    return gp_Dir(* self)


def compas_line_to_occ_line(self: Line) -> gp_Lin:
    return gp_Lin(self.start.to_occ_point(), self.direction.to_occ_direction())


Point.to_occ_point = compas_point_to_occ_point
Vector.to_occ_vector = compas_vector_to_occ_vector
Vector.to_occ_direction = compas_vector_to_occ_direction
Line.to_occ_line = compas_line_to_occ_line
